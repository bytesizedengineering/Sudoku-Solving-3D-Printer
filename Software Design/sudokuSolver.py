import serial
import time
import numpy as np
from PIL import Image
print("importing pytesseract")
import pytesseract
print("importing cv2")
import cv2


port = "/dev/ttyUSB0"
baudrate = 250000


cameraCaptureGcode = """G28			; home all axes
G0 G21 			; set units to millimeters
G90 			; Absolute Positioning
G0 F4000  		; Feedrate of 4000mm/min
G0 Z157		; Move Z above paper
G0 X110 Y209		; Move X and Y to start location
M150 R255 U255 B255 ; Turn on RGB LED to full brightness
G0 F2000  		; Feedrate of 2000mm/min

"""
cameraCaptureGcode = cameraCaptureGcode.split('\n')

serial = serial.Serial(port,baudrate)
if serial:
	print('Opening serial port ' + port)
else:
	print('error opening port ' + port)
	exit()
time.sleep(2)	
serial.flushInput()
for line in cameraCaptureGcode:
	if (line.find(';') >= 0):
		line = line[:line.index(';')]
	if (len(line) > 0 and line.isspace() == False):
		print('sending : ' + line.strip())
		serial.write((line + "\n").encode())
		reply = serial.readline().decode().strip()
		print('reply: ' + reply)
		while('echo:busy: processing' in reply):
			reply = serial.readline().decode().strip()
			print('reply: ' + reply)
input("Press Enter to continue...")


# define a video capture object
vid = cv2.VideoCapture(0)

# Capture a video frame
ret, frame = vid.read()

# Display the resulting frame
print("starting camera...")
#cv2.imshow('frame', frame)
if not ret:
	print("failed to grab frame")
	exit()
else:
	print("capturing image...")
	cv2.imwrite("puzzle.png",frame)

vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
input("Press Enter to continue...")

#Read image
print("reading image")
img = cv2.imread('puzzle.png',cv2.IMREAD_COLOR)
#img = cv2.imread('tesseractTest2.png',cv2.IMREAD_COLOR)

cv2.imwrite("puzzleGray.png",imgGray)
#ret, thresh = cv2.threshold(imgGray, 140, 255, 0)
#cv2.imwrite("thresh.png",thresh)
#im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#cv2.imwrite("contours.png",contours)
#cv2.imshow('thresh', thresh)
input("Press Enter to continue...")
print("converting image to string")
puzzleStart = pytesseract.image_to_string(img, config='-l eng --oem 3 --psm 11')
print(puzzleStart)
input("Press Enter to close the program...")
exit()

#puzzleStart = "700080010000040980083005067070052008600907004200830050410200530039070000060090001" # Websudoku 2,814,930,593
puzzleStart = "000710320042680079001004060504000031000201000910000602030500400470036290068042000" # Websudoku 8,089,011,079
#puzzleStart = "280070309600104007745080006064830100102009800000201930006050701508090020070402050" # -easy-20200531
#puzzleStart = "100020400035040900704000001800000000091032080000100097070900600000000000000450000" # -medium-20200531
#puzzleStart = "000006200030900604004001090000003007500010000300208000058040130000000029010000000" # -hard-20200531
#puzzleStart = "910780200027001894684000300000846001740059080009000050106093008000500706002070130" # -easy-20200601
#puzzleStart = "000832067000600200800700010010020000509004700000008000007000940000005000402000500" # -medium-20200601
#puzzleStart = "890070010620003050004000000060040200000085430000100000002700500900200100500400000" # -hard-20200601
#puzzleStart = "000010030009005008804006025000000600008004000120087000300900200065008000900000000" # -hard-20200602



if (len(puzzleStart) != 81):
	print("puzzle does not have 81 entries!")
	exit()
else:
	puzzle = list(puzzleStart)
	print("puzzle: " + str(puzzle))
	

while('0' in puzzle): # while puzzle is not solved
	puzzleRows = [puzzle[0:9], puzzle[9:18], puzzle[18:27], puzzle[27:36], puzzle[36:45], puzzle[45:54], puzzle[54:63], puzzle[63:72], puzzle[72:81]]
	#print("puzzleRows: " + str(puzzleRows)) 

	puzzleColumns = [puzzle[0:81:9], puzzle[1:81:9], puzzle[2:81:9], puzzle[3:81:9], puzzle[4:81:9], puzzle[5:81:9], puzzle[6:81:9], puzzle[7:81:9], puzzle[8:81:9]]
	#print("puzzleColumns: " + str(puzzleColumns))

	puzzleBoxes = [puzzle[0:3] + puzzle[9:12] + puzzle[18:21], 
	puzzle[3:6] + puzzle[12:15] + puzzle[21:24], 
	puzzle[6:9] + puzzle[15:18] + puzzle[24:27], 
	puzzle[27:30] + puzzle[36:39] + puzzle[45:48], 
	puzzle[30:33] + puzzle[39:42] + puzzle[48:51], 
	puzzle[33:36] + puzzle[42:45] + puzzle[51:54], 
	puzzle[54:57] + puzzle[63:66] + puzzle[72:75], 
	puzzle[57:60] + puzzle[66:69] + puzzle[75:78], 
	puzzle[60:63] + puzzle[69:72] + puzzle[78:81]]
	#print("puzzleBoxes: " + str(puzzleBoxes))

		
	candidates = ['']*81
	for cell in range(81): #loop through puzzle solution
		if puzzle[cell] == '0': # assign candidates for each unsolved cell
			column = cell%9
			row = cell//9 # quotient is not the same as division
			box = (column)//3 + (cell//27)*3
			for n in range(1,10): 
				n = str(n)
				if (n not in puzzleColumns[column] and n not in puzzleRows[row] and n not in puzzleBoxes[box]): 
					candidates[cell] += n #append n to candidates[cell]
			print ("cell " + str(cell) + " candidates: " + candidates[cell])	
			if len(candidates[cell]) == 1: #If a cell has only one candidate, place that value there (naked single).
				puzzle[cell] = str(candidates[cell])
			'''
			else:
				rowCandidates = []
				for item in range(cell - column,cell):
					rowCandidates += candidates[item]
				for item in range(cell + 1,cell + 9 - column):
					rowCandidates += candidates[item]
				
				columnCandidates = []
				for item in range(column,cell,9):
					columnCandidates += candidates[item]
				for item in range(cell + 9,72 + column,9):
					columnCandidates += candidates[item]
				
				for c in candidates[cell]: #If a candidate is unique within a row, box or column, place that value there (hidden single). 	
					if (c not in rowCandidates or c not in columnCandidates): # or c not in boxCandidates):
						puzzle[cell] = str(c)
						break
			'''
			
	print("puzzle: " + str(puzzle))


H_spacing = 13.0
V_spacing = 12.5
feedrate = 2000


headerGcode = """;G28			; home all axes
G0 G21 			; set units to millimeters
G90 			; Absolute Positioning
G0 F4000  		; Feedrate of 4000mm/min
G0 Z22.5		; Move Z up to 2mm above paper
G0 X94.4 Y211.7		; Move X and Y to start location
G91 			; Relative Positioning
G0 F2000  		; Feedrate of 2000mm/min

"""

number0 = """;number 0
G0 X-0.227 Y2.75
G0 Z-2
G0 X0.524 Y0
G0 X0.786 Y-0.262
G0 X0.524 Y-0.786
X0.262 Y-1.309
G0 X0 Y-0.786
G0 X-0.262 Y-1.309
G0 X-0.524 Y-0.786
G0 X-0.786 Y-0.262
G0 X-0.524 Y0
G0 X-0.785 Y0.262
G0 X-0.524 Y0.786
G0 X-0.262 Y1.309
G0 X0 Y0.786
G0 X0.262 Y1.309
G0 X0.524 Y0.786
G0 X0.785 Y0.262
G0 Z2
G0 X0.227 Y-2.75

"""

number1 = """;number 1
G0 X-0.75 Y1.702
G0 Z-2
G0 X0.523 Y0.262
G0 X0.786 Y0.786
G0 X0 Y-5.5
G0 Z2
G0 X-0.559 Y2.75

"""

number2 = """;number 2
G0 X-1.536 Y1.44
G0 Z-2
G0 X0 Y0.262
G0 X0.262 Y0.524
G0 X0.262 Y0.262
G0 X0.524 Y0.262
G0 X1.047 Y0
G0 X0.524 Y-0.262
G0 X0.262 Y-0.262
G0 X0.262 Y-0.524
G0 X0 Y-0.523
G0 X-0.262 Y-0.524
G0 X-0.524 Y-0.786
G0 X-2.619 Y-2.619
G0 X3.667 Y0
G0 Z2
G0 X-1.869 Y2.75

"""

number3 = """;number 3
G0 X-1.274 Y2.75
G0 Z-2
G0 X2.881 Y0
G0 X-1.572 Y-2.095
G0 X0.786 Y0
G0 X0.524 Y-0.262
G0 X0.262 Y-0.262
G0 X0.262 Y-0.786
G0 X0 Y-0.524
G0 X-0.262 Y-0.785
G0 X-0.524 Y-0.524
G0 X-0.786 Y-0.262
G0 X-0.785 Y0
G0 X-0.786 Y0.262
G0 X-0.262 Y0.262
G0 X-0.262 Y0.524
G0 Z2
G0 X1.798 Y1.702

"""

number4 = """;number 4
G0 X2.131 Y-0.917
G0 Z-2
G0 X-3.929 Y0
G0 X2.619 Y3.667
G0 X0 Y-5.5
G0 Z2
G0 X-0.821 Y2.75

"""

number5 = """;number 5
G0 X1.345 Y2.75
G0 Z-2
G0 X-2.619 Y0
G0 X-0.262 Y-2.357
G0 X0.262 Y0.262
G0 X0.786 Y0.262
G0 X0.785 Y0
G0 X0.786 Y-0.262
G0 X0.524 Y-0.524
G0 X0.262 Y-0.786
G0 X0 Y-0.524
G0 X-0.262 Y-0.785
G0 X-0.524 Y-0.524
G0 X-0.786 Y-0.262
G0 X-0.785 Y0
G0 X-0.786 Y0.262
G0 X-0.262 Y0.262
G0 X-0.262 Y0.524
G0 Z2
G0 X1.798 Y1.702

"""

number6 = """;number 6
G0 X-1.798 Y-0.917
G0 Z-2
G0 X0.262 Y0.786
G0 X0.524 Y0.524
G0 X0.785 Y0.262
G0 X0.262 Y0
G0 X0.786 Y-0.262
G0 X0.524 Y-0.524
G0 X0.262 Y-0.786
G0 X0 Y-0.262
G0 X-0.262 Y-0.785
G0 X-0.524 Y-0.524
G0 X-0.786 Y-0.262
G0 X-0.262 Y0
G0 X-0.785 Y0.262
G0 X-0.524 Y0.524
G0 X-0.262 Y1.047
G0 X0 Y1.31
G0 X0.262 Y1.309
G0 X0.524 Y0.786
G0 X0.785 Y0.262
G0 X0.524 Y0
G0 X0.786 Y-0.262
G0 X0.262 Y-0.524
G0 Z2
G0 X-1.345 Y-1.96

"""

number7 = """;number 7
G0 X-1.798 Y2.75
G0 Z-2
G0 X3.667 Y0
G0 X-2.619 Y-5.5
G0 Z2
G0 X0.75 Y2.75

"""

number8 = """;number 8
G0 X-0.488 Y2.75
G0 Z-2
G0 X-0.786 Y-0.262
G0 X-0.262 Y-0.524
G0 X0 Y-0.524
G0 X0.262 Y-0.523
G0 X0.524 Y-0.262
G0 X1.047 Y-0.262
G0 X0.786 Y-0.262
G0 X0.524 Y-0.524
G0 X0.262 Y-0.524
G0 X0 Y-0.785
G0 X-0.262 Y-0.524
G0 X-0.262 Y-0.262
G0 X-0.786 Y-0.262
G0 X-1.047 Y0
G0 X-0.786 Y0.262
G0 X-0.262 Y0.262
G0 X-0.262 Y0.524
G0 X0 Y0.785
G0 X0.262 Y0.524
G0 X0.524 Y0.524
G0 X0.785 Y0.262
G0 X1.048 Y0.262
G0 X0.524 Y0.262
G0 X0.262 Y0.523
G0 X0 Y0.524
G0 X-0.262 Y0.524
G0 X-0.786 Y0.262
G0 X-1.047 Y0
G0 Z2
G0 X0.488 Y-2.75

"""

number9 = """;number 9
G0 X1.607 Y0.917
G0 Z-2
G0 X-0.262 Y-0.786
G0 X-0.524 Y-0.524
G0 X-0.786 Y-0.262
G0 X-0.262 Y0
G0 X-0.785 Y0.262
G0 X-0.524 Y0.524
G0 X-0.262 Y0.786
G0 X0 Y0.262
G0 X0.262 Y0.785
G0 X0.524 Y0.524
G0 X0.785 Y0.262
G0 X0.262 Y0
G0 X0.786 Y-0.262
G0 X0.524 Y-0.524
G0 X0.262 Y-1.047
G0 X0 Y-1.31
G0 X-0.262 Y-1.309
G0 X-0.524 Y-0.786
G0 X-0.786 Y-0.262
G0 X-0.523 Y0
G0 X-0.786 Y0.262
G0 X-0.262 Y0.524
G0 Z2
G0 X1.536 Y1.964

"""

footerGcode = """G90 			; Absolute Positioning
G0 F4000  		; Feedrate of 4000mm/min
G0 Z200			; Move pen up
G0 X275 Y275		; Move pen to reveal paper
M84				; Disable steppers

"""




moveRightToNextCell = "G0 " + "X" + str(H_spacing) + "\t\t;move right to next cell\n\n"

moveToNewRow = "G0 F4000\t\t; Feedrate of 4000mm/min\n" + "G0 " + "X" + str(-8*H_spacing) + " Y" + str(-V_spacing) + "\t\t;move to new row\n" + "G0 F2000\t\t; Feedrate of 2000mm/min\n\n"

gcodeList = [number0, number1, number2, number3, number4, number5, number6, number7, number8, number9]


solutionGcode = headerGcode

for cell in range(81):
	solutionGcode += ";cell " + str(cell) + "\n"
	if puzzleStart[cell] == '0': # if the cell was empty at the start of the puzzle, fill in the cell 
			solutionGcode += gcodeList[int(puzzle[cell])]
	if (cell+1)%9 != 0: # move right to the next cell until it is the end of the row then move to new row
			solutionGcode += moveRightToNextCell
	else:
		solutionGcode += moveToNewRow
		
'''
for row in range(9):
	for x in gcodeList[1:len(gcodeList)]:
		solutionGcode += x
		if x != number9:
			solutionGcode += moveRightToNextCell
	if row != 8:
		solutionGcode += moveToNewRow
'''
solutionGcode += footerGcode

#print(solutionGcode)

f = open("solution.gcode", "w")
f.write(solutionGcode)
f.close()

#exit()

solutionGcode = solutionGcode.split('\n')

serial = serial.Serial(port,baudrate)
if serial:
	print('Opening serial port ' + port)
else:
	print('error opening port ' + port)
	exit()

time.sleep(2)
serial.flushInput()
for line in solutionGcode:
	if (line.find(';') >= 0):
		line = line[:line.index(';')]
	if (len(line) > 0 and line.isspace() == False):
		print('sending : ' + line.strip())
		serial.write((line + "\n").encode())
		print('reply: ' + serial.readline().decode().strip())
# Wait here until plotting is finished then close serial port.
input("Press Enter to close the program...")
serial.close()

