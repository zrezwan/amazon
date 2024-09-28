#!/usr/bin/env python
import os
import sys

# === CONFIG (TODO) ===

weightsConfig = ["amazon.config"] # Leave array empty or have one empty string if using no weights (if CMakeLists.txt has IS_CHECKER set to TRUE).
# If using weights (when CMakeLists.txt has IS_CHECKER set to FALSE), put config file names (i.e. "permutations.config", "company.config").
# general.config can be included if you want. It shouldn't affect program output.

gradeFileName = "GR2_hw-username.md" # File that `make grade` outputs the score to
# Should be GR<HW#>_hw-username.md

# === END OF CONFIG ===

testSuitePath = "build" # Path to test folder created and placed by nick.sh. Program is being executed at the root of the repository (i.e. "./build/", "./build", or "build")
totalPoints = None # Total combined points of all tests from each section (will be overrided)
totalTests = None # Total tests of all sections (will be overrided)
testSuiteNames = set() # Used for detecting when test suite name changes (i.e. Permutations to Company)
weights = {} # Stores weights associated to each test received from config files
testStdOutFiles = [] # Store file names that will be generated in hw#_tests/test-output for make grade parsing

deductionMessages = [] # Store deduction messages for compiler warnings and valgrind errors/warnings
totalDeductions = 0.0 # Total combined deductions for compiler warnings and valgrind errors/warnings

is_checker = None # Placeholder until it's changed to match what's in CMakeLists.txt
# True is for student-mode
# False is for grade-mode

# Basically just checks the boolean in set(IS_CHECKER <boolean>) from CMakeLists.txt. Can also retrieve other info if you want.
def parseCMakeListsTxt():
	global testSuitePath
	global is_checker
	global testStdOutFiles

	if len(testSuitePath) == 0:
		print("Error: testSuitePath is empty string")
		sys.exit(1)
	if testSuitePath[-1] != '/':
		testSuitePath += '/'
	cmakeliststxtFile = testSuitePath + "CMakeLists.txt"
	if not os.path.exists(cmakeliststxtFile):
		print("Error: Couldn't find CMakeLists.txt from project root with path:", cmakeliststxtFile)
		sys.exit(1)
	with open(cmakeliststxtFile) as f:
		while True:
			line = f.readline()
			if not line:
				break

			if "set" and "IS_CHECKER" in line:
				if "TRUE" in line: # Student-mode (no grade rubric or score output)
					is_checker = True
				elif "FALSE" in line: # Grading-mode. Will consider output of make grade for score calculation and deductions (like valgrind errors)
					is_checker = False
			elif "add_subdirectory" in line and ("testing_utils" not in line) and "_tests" in line:
				# Get names of testing directories. Important for finding stdout files like hw1_tests/test-output/permutations-test-stdout.txt
				# caused by "make grade". This program will parse those files if in grading mode.
				splits = line.split("(")
				line = splits[1]
				splits = line.split(")")
				line = splits[0].strip()
				line = line.split("_")[0].strip() # Should be the name we need like "permutations" for "build/test-output/permutations-test-stdout.txt"
				testStdOutFiles.append(testSuitePath + "test-output/" + line + "-test-stdout.txt")

# Parse config weights from files like rubric/permutations.config (defined by weightsConfig) within testSuitePath folder
def parseConfigFiles():
	global weightsConfig
	global testSuitePath
	global totalPoints
	global totalTests
	global weights
	global is_checker


	if is_checker == None or is_checker == True or len(weightsConfig) == 0: return # All values retrieved from  parseCMakeListsTxt()

	generalConfigFound = False
	for fileName in weightsConfig:
		if len(fileName) == 0:
			break
		if fileName == "general.config":
			generalConfigFound = True
			continue
		first = True
		fileName = testSuitePath + "rubric/" + fileName
		with open(fileName) as f: # Open the .config file
			while True:
				line = f.readline()
				if not line: # End-of-file
					break
				if first: # ignore first line (it will be like [test])
					first = False
					continue
				splits = line.strip().split() # Strip the whitespace then split by spaces
				weights[splits[0]] = float(splits[2]) # Ex: Permutations.CaseUSC = .5
	totalPoints = sum(weights.values()) # Add up all the value weights. Should handle decimals
	totalTests = len(weights) # The amount of key-value pairs in weights are the amount of tests we should have
	# if generalConfigFound == False:
	# 	print("Error: Couldn't find general.config file in rubric. Check that it's defined in the rubric folder and your weightsConfig array.")
	# 	sys.exit(1)
	if totalPoints == 0 or totalTests == 0:
		print(f"Error: Failed to parse test rubric weights. Got totalPoints={totalPoints} and totalTests={totalTests}")
		print("Some possible issues are:")
		print("1. Wrong testSuitePath. Can be caused by misnamed path in CONFIG section or mismatch with where nick.sh places test suite files")
		print("2. Missing rubric folder within test folder and/or non-general config files. Example structure:")
		print("ROOT\n\t.github\n\t\t...\n\tbuild\n\t\trubric\n\t\t\tgeneral.config\n\t\t\tpermutations.config\n\t\t\tcompany.config\n\t\tCMakeLists.txt\n\t\t...")
		print("3. Mismatch between file names and strings you wrote within weightsConfig")
		sys.exit(1)

# Retrieving Compiler warnings and Valgrind warnings/errors
# Format we look for is based on cs_grading/grading_tools.py when self._add_deduction() is called
def parseGradeReport():
	global testSuitePath
	global deductionMessages
	global totalDeductions
	global gradeFileName

	with open(testSuitePath + gradeFileName) as f: # Open the grade report file
		while True:
			line = f.readline()
			if not line: # End-of-file
				break
			
			# Ex: line = "+ (-1.0 points) Warning unused variable"
			splits = line.strip().split() # Strip the whitespace then split by spaces, so left with "(-1.0" from example
			if ('but warning deduction capped at' in line or
			'Warning' in line or
			'Valgrind error (should be' in line or
			'Valgrind error' in line):
				deductionMessages.append(line + "\n")
				totalDeductions += float(splits[1][1:]) # Ex: float("-1.0")

# Print a row spanning all column space with the name of the test suite (i.e. "Permutations", "CompanyInit", "CompanyMerge")
def printNewTestSuiteName(o, currTestSuiteName):
	o.write(f"<tr><td colspan='5'><b>{currTestSuiteName}</b></td></tr>\n")

def printTestCaseGrade(o, earned, points):
	o.write(f"<td>{earned}</td>\n") # Earned
	o.write(f"<td>{points}</td>\n") # Points (weight)

def printSubTotal(o, subGrade, subTotal):
	o.write(f"<tr><td></td><td><b>Subtotal</b></td><td>{subGrade}</td><td>{subTotal}</td><td></td></tr>\n")

def printTotalGrade(o, studentGrade, totalPoints):
	o.write(f"<tr><td colspan='2'><b>TOTAL</b></td><td><b>{studentGrade}</b></td><td><b>{totalPoints}</b></td><td></td></tr></table>\n\n")

# Print how many tests failed at the bottom of the table. Use for student-mode (non-grading)
def printTotalNumFailed(o, numFailed):
	o.write(f"<tr><td colspan='2'><b>FAILED {numFailed} tests</b></td><td></td></tr></table>\n\n")

# Note for students printed at the end of the summary in both is_checker modes
def printNote(o):
	o.write("Keep in mind there may be additional assignment-specific points mentioned by the writeup and Visual Inspection Rubric that graders will manually check.\n\n")

# Parse output from running ctest
def parseStudentMode():
	global weightsConfig
	global testSuitePath
	global totalPoints
	global totalTests
	global testSuiteNames
	global weights
	global is_checker
	global testStdOutFiles

	numFailed = 0

	# No longer using this since all weights should be defined within .config files in rubric folder (if grade-mode is on)
	# defaultWeight = round(totalPoints / totalTests, 2) # Round to the thousandths place

	studentGrade = 0
	o = open('ctest_output_pretty.txt', 'w')
	o.write("## Grade Report\n")
	if is_checker == False: # Grading-mode
		o.write("<table><thead><tr><td><b>Result</b></td><td><b>Test</b></td><td><b>Earned</b></td><td><b>Points</b></td><td><b>Details</b></td></tr></thead>\n")
	else: # Student-mode (non-grading)
		o.write("<table><thead><tr><td><b>Result</b></td><td><b>Test</b></td><td><b>Details</b></td></tr></thead>\n")
	
	with open(testSuitePath + 'ctest_output.txt') as f: # Ex: build/ctest_output.txt or ./build/ctest_output.txt
		isFirst = True
		fatalError = False
		subTotal = 0
		subGrade = 0
		currTestSuiteName = ""
		line = ""
		dont_read = False
		while True:
			if not dont_read:
				line = f.readline()
			dont_read = False
			if fatalError or not line:
				break

			if 'Start' in line and isFirst: # First test category
				splits = line.split(".")
				currTestSuiteName = splits[0].split()[2]
				printNewTestSuiteName(o, currTestSuiteName)
				testSuiteNames.add(currTestSuiteName)
				isFirst = False
			elif 'Start' in line: # Second or later test category, need to print subtotal from previous category
				splits = line.split(".")
				currTestSuiteName = splits[0].split()[2]
				if currTestSuiteName not in testSuiteNames: # New test suite name (new category of problems)
					if is_checker == False: # If in grade-mode
						printSubTotal(o, subGrade, subTotal)
					printNewTestSuiteName(o, currTestSuiteName)
					testSuiteNames.add(currTestSuiteName)
					subTotal = 0
					subGrade = 0
			elif 'Passed' in line:
				o.write("<tr><td>✅ PASS</td>\n")
				
				tempLine = line.split(f"{currTestSuiteName}.")[1] # Split should be something like [" 5/23 Test  #5: ", "SingleItemNonempty ............   Passed    0.62 sec"]
				splits = tempLine.split() # Split by spaces
				o.write(f"<td>{splits[0]}</td>\n") # Test name
				if is_checker == False: # If in grade-mode
					currWeight = weights[f"{currTestSuiteName}.{splits[0]}"]
					studentGrade += currWeight
					subTotal += currWeight
					subGrade += currWeight
					printTestCaseGrade(o, currWeight, currWeight)
				o.write("<td></td>\n") # Details (empty on passing test)
				o.write("</tr>\n")
			elif '***Failed' in line or '***Not Run' in line: # Not sure if there can be duplicates within the same test
				numFailed += 1
				o.write("<tr><td>❌ FAIL</td>\n")

				tempLine = line.split(f"{currTestSuiteName}.")[1]
				splits = tempLine.split() # Split by spaces
				o.write(f"<td>{splits[0]}</td>\n") # Test name
				if is_checker == False: # If in grade-mode
					currWeight = weights[f"{currTestSuiteName}.{splits[0]}"]
					subTotal += currWeight
					printTestCaseGrade(o, "0", currWeight)
				o.write("<td><details closed><summary>Failure Info</summary>\n")
				o.write("<pre>\n")
				errorMessage = ""
				if '***Not Run' in line:
					errorMessage = "Test case did not run, likely due to compile error. If there is no compile error, please read the output from (build --> Build and run tests)"
					o.write(errorMessage) # Error message
					o.write("</pre></details></td>\n")
					o.write("</tr>\n")
					continue
				while True:
					line = f.readline()
					if not line: 
						fatalError = True # For outer while loop
						break

					if 'ERROR SUMMARY' in line: # End of failed test output
						errorMessage += line
						break
					elif 'Start' in line or '***Failed' in line or '***Not Run' in line: # New test output
						dont_read = True # Don't read in a line from output since I already have what I need
						break
					errorMessage += line
				if(len(errorMessage) == 0):
					errorMessage = "Unable to parse error, please read the output from (build --> Build and run tests)"
				o.write(errorMessage) # Error message
				o.write("</pre></details></td>\n")
				o.write("</tr>\n")
		# end-while
		if is_checker == False and len(testSuiteNames) >= 2: # Edge case (last test suite should also get a subtotal if there's multiple)
			printSubTotal(o, subGrade, subTotal)
			subTotal = 0
			subGrade = 0
		
		if is_checker == False: # In grade-mode
			studentGrade = min(totalPoints, round(studentGrade, 2)) # In case weights add up to slightly over total amount (due to rounding)
			printTotalGrade(o, studentGrade, totalPoints)
		else: # In student-mode (non-grading)
			printTotalNumFailed(o, numFailed)
		
		if(numFailed >= 1):
			o.write("## 🚨🚨 Some test cases failed!! 😭😭\n\n")
		if is_checker == False: # In grade-mode
			studentGrade = max(0, studentGrade) # Prevents negative scores
			o.write(f"You received {studentGrade} out of {totalPoints} points.\n\n")
			print(f"You received {studentGrade} out of {totalPoints} points.\n\n")
		else: # In student-mode (non-grading)
			o.write("Grade score is disabled on this assignment. Make sure there are no valgrind errors (in the build tab on the left) since those may result in large deductions.\n\n")
		printNote(o)
		o.close() # Close the output file
		f.close() # Close the input file

# Parse output from running make grade
def parseGradingMode():
	global weightsConfig
	global testSuitePath
	global totalPoints
	global totalTests
	global testSuiteNames
	global weights
	global is_checker
	global testStdOutFiles

	numFailed = 0

	# No longer using this since all weights should be defined within .config files in rubric folder (if grade-mode is on)
	# defaultWeight = round(totalPoints / totalTests, 2) # Round to the thousandths place

	studentGrade = 0
	o = open('ctest_output_pretty.txt', 'w')
	o.write("## Grade Report\n")
	o.write("<table><thead><tr><td><b>Result</b></td><td><b>Test</b></td><td><b>Earned</b></td><td><b>Points</b></td><td><b>Details</b></td></tr></thead>\n")

	for fileName in testStdOutFiles:
		if not os.path.exists(fileName):
			print(f"Warning: {fileName} not found. Going to next file for test stdout.")
			continue
		with open(fileName) as f: # Ex: build/test-output/permutations-test-stdout.txt or ./build/test-output/company-test-stdout.txt
			isFirst = True
			fatalError = False
			subTotal = 0
			subGrade = 0
			currTestSuiteName = ""
			line = ""
			dont_read = False
			testCaseName = ""
			testOutput = ""
			testPassed = True
			print("\n\n\nTo look at the following file locally. Please do \"make grade\" in your test directory. Then look at the .txt files in test_directory/test-output")
			print(f"##### Output from {fileName} #####")
			while True:
				line = f.readline()

				if not line:
					break
				print(line) # Print contents of file to terminal so students can view raw output on GitHub Actions

				if 'OUTPUT OF TEST' in line:
					# Deal with old test stuff
					if not testPassed: # Never saw the passing message (so assuming failure)
						numFailed += 1
						o.write("<tr><td>❌ FAIL</td>\n")

						o.write(f"<td>{testCaseName}</td>\n") # Test name
						currWeight = weights[f"{currTestSuiteName}.{testCaseName}"]
						subTotal += currWeight
						printTestCaseGrade(o, "0", currWeight)
						o.write("<td><details closed><summary>Failure Info</summary>\n")
						o.write("<pre>\n")
						
						if(len(testOutput) == 0):
							testOutput = "Unable to parse error, please read the output from (build --> Build and run tests)"
						o.write(testOutput) # Error message
						o.write("</pre></details></td>\n")
						o.write("</tr>\n")
					testPassed = False

					# Get new test info
					splits = line.split()[3].split('.')
					currTestSuiteName = splits[0]
					testCaseName = splits[1].strip()[:-1] # Trim the newline and the ':' at the end
					testOutput = ""

					# Print Subtotal of old test stuff and new Test Suite Name if found
					if currTestSuiteName not in testSuiteNames:
						if not isFirst: # Don't print a subtotal on top of the first test suite output
							printSubTotal(o, subGrade, subTotal)
						isFirst = False
						printNewTestSuiteName(o, currTestSuiteName)
						testSuiteNames.add(currTestSuiteName)
						subTotal = 0
						subGrade = 0
				else:
					testOutput += line
					if '[       OK ]' in line: # Passed the test
						testPassed = True

						o.write("<tr><td>✅ PASS</td>\n")
						o.write(f"<td>{testCaseName}</td>") # Test name
						currWeight = weights[f"{currTestSuiteName}.{testCaseName}"]
						studentGrade += currWeight
						subTotal += currWeight
						subGrade += currWeight
						printTestCaseGrade(o, currWeight, currWeight)
						o.write("<td></td>\n") # Details (empty on passing test)
						o.write("</tr>\n")
			# end-while
			# Output info related to last test in section
			if not testPassed: # Never saw the passing message (so assuming failure)
				numFailed += 1
				o.write("<tr><td>❌ FAIL</td>\n")

				o.write(f"<td>{testCaseName}</td>\n") # Test name
				currWeight = weights[f"{currTestSuiteName}.{testCaseName}"]
				subTotal += currWeight
				printTestCaseGrade(o, "0", currWeight)
				o.write("<td><details closed><summary>Failure Info</summary>\n")
				o.write("<pre>\n")
				
				if(len(testOutput) == 0):
					testOutput = "Unable to parse error, please read the output from (build --> Build and run tests)"
				o.write(testOutput) # Error message
				o.write("</pre></details></td>\n")
				o.write("</tr>\n")
			if fileName != testStdOutFiles[-1]: # Only print subtotal if I'm still going to parse another file
				printSubTotal(o, subGrade, subTotal)
				subGrade = 0
				subTotal = 0
		# end-with
	# end-for
	f.close() # Close the input file
	if len(testSuiteNames) >= 2: # Edge case (last test suite should also get a subtotal if there's multiple)
		printSubTotal(o, subGrade, subTotal)
		subTotal = 0
		subGrade = 0
	
	studentGrade = min(totalPoints, round(studentGrade, 2)) # In case weights add up to slightly over total amount (due to rounding)
	printTotalGrade(o, studentGrade, totalPoints)
	
	if(numFailed >= 1):
		o.write("## 🚨🚨 Some test cases failed!! 😭😭\n\n")

	parseGradeReport()
	if totalDeductions != 0.0:
		studentGrade += totalDeductions
		o.write("## 🚨🚨 Automatic Deductions Received:\n\n")
		print("\nAutomatic Deductions Received:\n\n")
		for message in deductionMessages:
			o.write(f"{message}\n")
			print(f"{message}")
		o.write("+ Note that automatic deductions only check for compiler warnings, and Valgrind errors\n\n")
		print("+ Note that automatic deductions only check for compiler warnings, and Valgrind errors\n")

	studentGrade = max(0, studentGrade) # Prevents negative scores
	o.write(f"You received {studentGrade} out of {totalPoints} automatic points.\n\n")
	print(f"You received {studentGrade} out of {totalPoints} automatic points.\n\n")
	printNote(o)
	o.close() # Close the output file
	if(numFailed >= 1): # If a test failed, change exit status for nick.sh
		exit(1)

def main():
	global weightsConfig
	global testSuitePath
	global totalPoints
	global totalTests
	global testSuiteNames
	global weights
	global is_checker
	global testStdOutFiles

	cwd = os.getcwd()
	print(cwd)

	parseCMakeListsTxt()
	if is_checker == None:
		print("Warning: Couldn't find IS_CHECKER in CMakeLists.txt. Assuming no grade weights are being used.")
		is_checker = True
	parseConfigFiles()

	if is_checker == True:
		parseStudentMode()
	else:
		parseGradingMode()

if __name__ == '__main__':
	main()