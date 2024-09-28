#!/bin/bash
# Cmake into build directory
# curl -L -O http://chalonverse.com/435/pa1.tar.gz || { echo "::error::Unable to download graded tests. Try again."; exit 1; }
# tar xzf pa1.tar.gz || { echo "::error::Error downloading graded tests. Try again."; exit 1; }
echo "Compiling..."
mkdir build
cd build

# TODO: Get test files so that you can do cmake . within build directory. You may need to edit the curl file source
curl -L -O https://bytes.usc.edu/cs104/homework/test-suites/hw2_tests.tar.gz || { echo "::error::Unable to download graded tests. Try again."; exit 1; }
tar xvf hw2_tests.tar.gz || { echo "::error::Error downloading graded tests. Try again."; exit 1; }
cp -rf ./hw2_tests/* .

# Put the name of each target (probably the name of the test .cpp files) here for compiling separately. Like "make permutations_tests".
# Leave as an empty array if you just want plain "make" to be used. If using empty array and there are multiple targets, the failure of the first target compiling,
# will result in other targets not compiling. For example, if permutations_tests has a compile error, company_tests won't compile as well.
test_directories=("amazon_tests") # Won't be used in Grading-mode
# End TODO

cmake . || exit 1
build_failed=0
build_success_counter=0
compile_errors=0


# Run test cases
tests_failed=0
if grep -q 'set(IS_CHECKER FALSE)' CMakeLists.txt; then # Grading-mode
	echo -e "Running tests in grading-mode"
	make grade

	if [ ! -d "./compile-logs"]; then
		echo "Couldn't find compile-logs directory. Unable to give compiler warning info"
	fi

	# Get each file
	rm -rf diagnostics.txt
	for log_file in "./compile-logs"/*.complog; do
		if [ -f "$log_file" ]; then
			cat "$log_file" >> "diagnostics.txt"
		fi
	done

	if [ "${PIPESTATUS[0]}" -ne "0" ] ; then # Nothing compiled correctly
		echo "::error::Code did not compile!"
		echo -e "## \xF0\x9F\x9A\xA8\xF0\x9F\x9A\xA8 Code did not compile!! Your grade is currently a 0!! \xF0\x9F\x98\xAD\xF0\x9F\x98\xAD" >> ${GITHUB_STEP_SUMMARY}
		echo "### Build Log"  >> ${GITHUB_STEP_SUMMARY}
		echo -n "<pre>" >> ${GITHUB_STEP_SUMMARY}
		cat diagnostics.txt >> ${GITHUB_STEP_SUMMARY}
		echo "</pre>" >> ${GITHUB_STEP_SUMMARY}
		build_failed=1
	fi
	cd ..
	chmod +x ./.github/helpers/diagnostics-json.py
	python3 ./.github/helpers/diagnostics-json.py # Parse compilation warnings and errors for Build Annotations workflow
	if [[ "$build_failed" == 1 ]] ; then
		exit 1
	fi
elif grep -q 'set(IS_CHECKER TRUE)' CMakeLists.txt; then  # Student-mode (no grade rubric or score output)
	if [ ${#test_directories[@]} -eq 0 ] ; then # Do just "make" if targets aren't specified
		make 2> >(tee diagnostics.txt >&2)
		if [ "${PIPESTATUS[0]}" -eq "0" ] ; then # Successful compilation
			((build_success_counter++))
		fi
	else
		for testDIR in ${test_directories[@]}; do # Loop over the make targets and compile them one-by-one. Also output each result into diagnostics.txt
			make $testDIR 2> >(tee -a diagnostics.txt >&2) # -a Appends to file
			if [ "${PIPESTATUS[0]}" -ne "0" ] ; then # Unsuccessful compilation
				((compile_errors++))
			else
				((build_success_counter++))
			fi
		done
	fi

	if [ $build_success_counter -eq 0 ] ; then # Nothing compiled correctly
		echo "::error::Code did not compile!"
		echo -e "## \xF0\x9F\x9A\xA8\xF0\x9F\x9A\xA8 Code did not compile!! Your grade is currently a 0!! \xF0\x9F\x98\xAD\xF0\x9F\x98\xAD" >> ${GITHUB_STEP_SUMMARY}
		echo "### Build Log"  >> ${GITHUB_STEP_SUMMARY}
		echo -n "<pre>" >> ${GITHUB_STEP_SUMMARY}
		cat diagnostics.txt >> ${GITHUB_STEP_SUMMARY}
		echo "</pre>" >> ${GITHUB_STEP_SUMMARY}
		build_failed=1
	elif [ $compile_errors -ne 0 ] ; then # Something compiled correctly but not all test directories
		echo "::error::Some code did not compile!"
	fi

	cd ..
	chmod +x ./.github/helpers/diagnostics-json.py
	python3 ./.github/helpers/diagnostics-json.py # Parse compilation warnings and errors for Build Annotations workflow
	if [[ "$build_failed" == 1 ]] ; then
		exit 1
	fi

	cd build

	echo -e "Running tests in student-mode" # (non-grading)
	ctest --output-on-failure | tee ctest_output.txt # "| tee <file>"" pipes output of ctest command

	if [ "${PIPESTATUS[0]}" -ne "0" ] ; then # If a test failed in student mode
		tests_failed=1
	fi
	
	cd ..
else
	echo "::error::Couldn't parse value of IS_CHECKER within build/CMakeLists.txt. Make sure it is in either written as exactly set(IS_CHECKER FALSE) or set(IS_CHECKER TRUE)."
	exit 1
fi

chmod +x ./.github/helpers/parse-ctest-out.py
# python3 ./.github/helpers/parse-ctest-out.py $errorCount
python3 ./.github/helpers/parse-ctest-out.py

if [ "${PIPESTATUS[0]}" -ne "0" ] ; then # If a test failed in grading mode (make grade doesn't set this variable so I did it in the python program)
	tests_failed=1
fi

# Print prettified test results
cat ctest_output_pretty.txt >> ${GITHUB_STEP_SUMMARY}

cd build
echo -e "\n## Compiler Errors & Warnings" >> ${GITHUB_STEP_SUMMARY}
if [ $compile_errors -ne 0 ] ; then # Can only be possible in non-grading mode
	echo -e "\xF0\x9F\x9A\xA8 Some code did not compile" >> ${GITHUB_STEP_SUMMARY}
fi

if grep -q error: diagnostics.txt && grep -q 'set(IS_CHECKER FALSE)' CMakeLists.txt; then # If a compile error was found in grading-mode
	echo -e "\xF0\x9F\x9A\xA8 There are compiler errors\n" >> ${GITHUB_STEP_SUMMARY}
	echo -en "<details closed><summary>Build Log</summary><pre>" >> ${GITHUB_STEP_SUMMARY}
	cat diagnostics.txt >> ${GITHUB_STEP_SUMMARY}
	echo -e "</pre></details>\n" >> ${GITHUB_STEP_SUMMARY}
elif grep -q warning diagnostics.txt; then # If a compile warning was found in either mode
	echo -e "\xE2\x9A\xA0 There are compiler warnings\n" >> ${GITHUB_STEP_SUMMARY}
	echo -en "<details closed><summary>Build Log</summary><pre>" >> ${GITHUB_STEP_SUMMARY}
	cat diagnostics.txt >> ${GITHUB_STEP_SUMMARY}
	echo -e "</pre></details>\n" >> ${GITHUB_STEP_SUMMARY}
else
	echo -e "\xE2\x9C\x85 There were no compiler warnings\n" >> ${GITHUB_STEP_SUMMARY}
fi

if [[ "$tests_failed" == 1 ]] ; then
	echo "::error::Not all graded tests passed!"
	exit 1
fi