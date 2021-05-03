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

original_x = []
original_y = []

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
		original_x.append(adc);
		original_y.append(tmp);
		if (len(all_data) == 0 or all_data[-1][0] != tmp):
			all_data.append([tmp, [adc]])
		else:
			all_data[-1][1].append(adc)



for i in range(len(all_data)):
	fig, ax = plt.subplots()
	if (len(all_data[i][1])):
		avg = int(sum(all_data[i][1])/len(all_data[i][1]))
		diff_array = [(avg-x)**2 for x in all_data[i][1]]
		stdev = np.sqrt(sum(diff_array)/len(all_data[i][1]))

		new_sum = []

		for j in range(len(all_data[i][1])):
			if abs(all_data[i][1][j] - avg) < stdev:
				new_sum.append(all_data[i][1][j])
		ax.scatter(all_data[i][1], [all_data[i][0] for k in range(len(all_data[i][1]))], label = 'original' + str(i))
		ax.scatter(new_sum,  [all_data[i][0] for k in range(len(new_sum))], label ='processed' + str(i))
	
#		print("stdev", stdev)
		if (len(new_sum)):
			all_data[i][1] = int(sum(new_sum)/len(new_sum))
		else:
			aLL_data[i][1] = 0

				
		print ("avg_original ", avg, "new avg ", all_data[i][1])


#	ax.legend()
#	plt.show()

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
	plt.scatter(original_x, original_y, marker = '.', )
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


