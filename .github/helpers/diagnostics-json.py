#!/usr/bin/env python
import json
import os
	
def main():
	cwd = os.getcwd()
	print(cwd)
	errorCount = 0
	with open('build/diagnostics.txt') as f:
		jsonOut = []
		while True:
			line = f.readline()
			if not line:
				break

			#print(line)
			if 'warning:' in line or 'error:' in line:
				splits = line.split(':')
				if len(splits) > 4:
					#print(splits)
					filePath = splits[0]
					filePath = filePath.replace(cwd + '/', '')
					
					iserror = False if splits[3] == " warning" else True
					
					try:
						message = ''
						message_split = []
						if iserror:
							message_split = line.split('error:')
						else:
							message_split = line.split('warning:')
						if len(message_split) > 1:
							message = message_split[1]
						
						message = message[1:-1]
						if message == '':
							message = 'Unknown warning or error, check log []'
						
						if not(iserror):
							messageSplits = message.rpartition('[')
							message = messageSplits[0]
						
						
						jsonOut.append({
							'file': filePath,
							'line': int(splits[1]),
							'title': 'Build Warning' if not (iserror) else 'Build Error',
							'message': message,
							'annotation_level': 'warning' if not(iserror) else 'failure'
						})
						errorCount += 1
					except:
						jsonOut.append({
							'file': filePath,
							'line': 1,
							'title': 'Build Warning' if not (iserror) else 'Build Error',
							'message': 'Failed to generate annotation for this warning/error. Please check the actions build log.',
							'annotation_level': 'warning' if not(iserror) else 'failure'
						})
						errorCount += 1
						pass	
		jsonStr = json.dumps(jsonOut, indent=2)
		#print(jsonStr)
		with open('diagnostics.json', 'w') as outFile:
			outFile.write(jsonStr)

		## Was used for getting the number of compile errors on parse-ctest-out.py but this is no longer needed
		# with open('build/errorCount.txt', 'w') as outFile2: # Will be used by nick.sh
		# 	outFile2.write(str(errorCount))
	
if __name__ == '__main__':
	main()
