import csv
import sys
import scipy
from scipy.optimize import curve_fit
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

header="// Auto generated file \n #ifndef IR_CONSTANTS\n #define IR_CONSTANTS\n\n"
footer = "#endif\n"

all_data = []

K = 0.75 # Constant for outlier removal

plot = int(sys.argv[3])


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
print ("\t Old \t\t New");
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
			ax.scatter(adc_readings, [ temp for k in range (len_adc)], label = 'original' + str(i), marker = '+')
			ax.scatter(adc_good,  [temp for k in range(len(adc_good))], label ='processed' + str(i), marker = 'x')

		
	
#		print("stdev", stdev)
		if (len(adc_good)):
			all_data[i][1] = int(sum(adc_good)/len(adc_good))
		else:
			all_data[i][1] = 0

				
		new_stdev = np.std(adc_good);
		print ("\t ", avg, " \t\t ", all_data[i][1])
		print ("\t ", round(stdev, 2), " \t\t ", round(new_stdev,2));


	if (plot > 1):
		ax.legend()
		plt.show()

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

if (plot):
	plt.scatter(xcurve, ycurve)
	plt.scatter(x_values, y_values);
	plt.show()

outfile = open(sys.argv[2], 'w')

outfile.write(header);
outfile.write("#define IR_CALIB_A " + str(a*100000) + "\n");
outfile.write("#define IR_CALIB_B " + str(b) + "\n");
outfile.write("#define IR_CALIB_C " + str(c) + "\n");

outfile.write(footer);

outfile.close();


