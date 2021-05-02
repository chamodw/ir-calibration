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

plot = int(sys.argv[3])



with open(sys.argv[1]) as csv_file:
	readCSV = csv.reader(csv_file, delimiter = ',')
	for row in readCSV:
		print (row)
		if (len(row) < 15):
			continue
		if (int(row[2]) == 265):
			ADC_ROW = 5; # Already calibrated sensor has ADC data on packet[1]
		else:
			ADC_ROW = 6; # Original sensor (type 2) has ADC data on packet[2]
		if (len(row) < 15):
			continue
		tmp = float(row[0])
		adc = int(row[ADC_ROW])
		if (len(all_data) == 0 or all_data[-1][0] != tmp):
			all_data.append([tmp, [adc]])
		else:
			all_data[-1][1].append(adc)



for i in range(len(all_data)):
	if (len(all_data[i][1])):
		all_data[i][1] = int(sum(all_data[i][1])/len(all_data[i][1]))

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


