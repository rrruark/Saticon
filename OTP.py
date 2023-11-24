import pandas as pd
import matplotlib.pyplot as plt
from math import floor

#Reads in CSV. CSV should have a header. Adjust voltage levels as needed to suite the source data.
df = pd.read_csv('CSV00.csv', sep=',')

#Trigger levels
v_rising = 0.04
v_falling = 0.02

#Extracts voltage data and discards time references
y=df['voltage']

#State tracking variable
high=0

#Empty array that will contain random bits
triggered=[]

#Triggers on the rising edge of events exceeding v_rising and does not allow for retriggering until voltage drops below v_falling.
for i in range(len(y)):
	if high==0:
		if y[i]>v_rising:
			#The LSB of the event index is stored as the random bit output.
			triggered.append(i%2)
			high=1
	else:
		if y[i]<v_falling:
			high=0
#print(triggered)

#State tracking variables
workingbyte=0
bitIndex=0

#Empty array that will contain random chracters
randchar = []

#Constructs five bit words from random data and saves them as ASCII characters.
for i in range(len(triggered)):
	if(triggered[i] > 0):
		workingbyte|=1<<bitIndex
	bitIndex+=1
	if(bitIndex==5):
		#This discards anything over 25 to keep only alpha characters
		if(workingbyte < 26):
			#Adds ASCII 'A' to make five bit words into 8 bit bytes from 'A' to 'Z'
			randchar.append(chr((workingbyte)+ord('A')))
			bitIndex=0
			workingbyte=0
		else:
			bitIndex=0
			workingbyte=0			

#Output file			
f = open("otp.txt", "w")

#String of all random characters
rand_str = ''.join([x for x in randchar])

#Adds spaces and line breaks to create groups of five characters with five groups per line.
group_count_total = floor(len(rand_str) / 5)
index = 0
out_str = ''
for i in range(group_count_total):
	group = rand_str[index:index + 5]
	index += 5
	
	out_str += group + ' '
	
	if ((i+1) % 5 == 0 and i != 0):
		out_str += '\r\n'
		
	
print(out_str)

#Writes string to output file.
f = open("otp.txt", "w")	
f.write(out_str)
f.close()