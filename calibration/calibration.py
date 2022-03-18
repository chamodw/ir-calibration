import csv
import sys
import scipy
from scipy.optimize import curve_fit
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

header="// Auto generated file \n #ifndef IR_CONSTANTS\n #define IR_CONSTANTS\n\n"
footer = "#endif\n"

stdev_limits=[8,8,30]

all_data = []

K = 0.75 # Constant for outlier removal

plot = int(sys.argv[2])


# Opens the data files and goes through each line
# Each file contains multiple sessions, each session has multiple lines with same temperature reading
# This loop first identifies the sensor type (Original or already calibrated), and then reads the temperature and ADC
# And then it rearranges in to the following structure
# [
# [ temp_0, [adc0, adc1, adc2, ..., adcn]], 
# [ temp_1, [adc0, adc1, adc2, ..., adcn]]
# ]


with open(sys.argv[1]) as csv_file:
	readCSV = csv.reader(csv_file, delimiter = ',')
	for row in readCSV:
		# Identify sensor type
		if (len(row) < 15):
			continue
		if (int(row[2]) == 265):
			ADC_ROW = 5; # Already calibrated sensor has ADC data on packet[1]
		else:
			ADC_ROW = 6; # Original sensor (type 2) has ADC data on packet[2]
		tmp = float(row[0]) # User input temperature reading 
		adc = int(row[ADC_ROW]) #ADC Reading
		if (len(all_data) == 0 or all_data[-1][0] != tmp): #Cluster data into same temperature groups
			all_data.append([tmp, [adc]])
		else:
			all_data[-1][1].append(adc)


# Remove outliers
print ("\t\tRaw\t Filtered");
for i in range(len(all_data)):

	if (plot > 1):
		fig, ax = plt.subplots()

	adc_readings = all_data[i][1]
	temp = all_data[i][0] 
	len_adc = len(adc_readings)

	if (len_adc):
		avg = int(sum(adc_readings)/len_adc)
		diff_array = [(avg-x)**2 for x in adc_readings] # (x^2 - mean) array for calculationg standard deviation
		stdev = np.sqrt(sum(diff_array)/len_adc)



		adc_good = []
		# Pick values that are within += K*stdev of mean and add to a new array

	
		for j in range(len_adc):
			if abs(adc_readings[j] - avg) < K*stdev: #Within accepted range
				adc_good.append(adc_readings[j])

		if (plot > 1):
			ax.plot(adc_readings, [ temp for k in range (len_adc)], label = 'original' + str(i), marker = '+')
			ax.scatter(adc_good,  [temp for k in range(len(adc_good))], label ='processed' + str(i), marker = 'x')

		
	
#		print("stdev", stdev)
		if (len(adc_good)):
			all_data[i][1] = int(sum(adc_good)/len(adc_good))
		else:
			all_data[i][1] = 0

				
		new_stdev = np.std(adc_good);
		print (all_data[i][0], "\tmean\t", avg, "\t", all_data[i][1])
		print (all_data[i][0], "\tstdev\t", round(stdev, 2), "\t", round(new_stdev,2));
		print ('-'*40);
	

		stdev_limit=8
		if (temp < 10):
			stdev_limit=stdev_limits[0]
		elif (temp < 40):
			stdev_limit=stdev_limits[1]
		else	:
			stdev_limit=stdev_limits[2]
	
		ex = 0
		if (new_stdev >= stdev_limit):
			print ("\033[0;31m ***Error too high! ***"); #print error in red
			print ("*** Continue programming the sensor? (y/n) *** \033[0m");
			#inp = input();
			#if (inp != 'y'):
#			exit(1)
			ex = 1



	if (plot > 1):
		ax.legend()
		plt.show()
	if (ex):
		exit(1)
if (len(sys.argv) < 4):
	exit()
if (len(all_data) < 3):
		print ("\033[0;31m ***Error: Not enough datapoints ***"); #print error in red
		print ("*** Continue programming the sensor? (y/n) *** \033[0m");
		inp = input();
		print (inp)
		if (inp != 'y'):
			exit(1)


x_values = [all_data[i][1] for i in range(len(all_data))]
y_values = [all_data[i][0] for i in range(len(all_data))]


def objective(X, a, b, c):
	return a*X**2 + b*X + c;


print (x_values)
print (y_values)

popt, _ = curve_fit(objective, x_values, y_values)
a, b, c = popt
print(a)
print(b)
print(c)


xcurve = range(min(x_values), max(x_values))
ycurve = [objective(i, a, b, c) for i in xcurve]

if (plot> 0):
	plt.scatter(xcurve, ycurve)
	plt.scatter(x_values, y_values);
	plt.show()

if (len(sys.argv) < 4):
	exit()
outfile = open(sys.argv[3], 'w')

outfile.write(header);
outfile.write("#define IR_CALIB_A " + str(a*100000) + "\n");
outfile.write("#define IR_CALIB_B " + str(b) + "\n");
outfile.write("#define IR_CALIB_C " + str(c) + "\n");

outfile.write(footer);

outfile.close();


