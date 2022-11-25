from numpy.polynomial import Polynomial
import matplotlib.pyplot as plt

# Recreated from original datasheet with http://www.graphreader.com/

# JDG12 100 Ah 0.1C Capacity vs time 100% DoD
capacity_vs_time_x = [0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13, 15, 17, 19, 22, 23, 24]
capacity_vs_time_y = [0.0, 12.824, 28.168, 40.305, 52.214, 62.29, 70.992, 77.405, 87.71, 94.809, 99.618, 102.595, 104.656, 106.031, 107.905, 109.021, 110.0]

try:
    capacity_vs_time_p_fitted = Polynomial.fit(x=capacity_vs_time_x, y=capacity_vs_time_y, deg=3)
    if callable(capacity_vs_time_p_fitted.convert):
        d, c, b, a = capacity_vs_time_p_fitted.convert().coef

        a = round(a, 3)
        b = round(b, 3)
        c = round(c, 3)
        d = round(d, 3)
        print(str(a) + " * x^3 + " + str(b) + " * x^2 + " + str(c) + " * x + " + str(d) + " = y")

        plt.clf()
        plt.title("Capacity vs time")
        plt.plot(capacity_vs_time_x, capacity_vs_time_y, linewidth=3, c="b")
        for x_val in capacity_vs_time_x:
            y_val = a * x_val * x_val * x_val + b * x_val * x_val + c * x_val + d
            plt.scatter(x_val, y_val, c="r")
        plt.show()
        plt.clf()
    else:
        print("Can't fit polynomial")
except Exception as e:
    print(str(e))


# JDG12 100 Ah 0.1C Voltage vs time 100% DoD
voltage_vs_time_x = [0, 1, 2, 3, 4, 5, 6, 7, 8]
voltage_vs_time_y = [11.8, 11.935, 12.138, 12.336, 12.542, 12.757, 13.117, 13.727, 14.2]
try:
    voltage_vs_time_p_fitted = Polynomial.fit(x=voltage_vs_time_x, y=voltage_vs_time_y, deg=3)
    if callable(voltage_vs_time_p_fitted.convert):
        d, c, b, a = voltage_vs_time_p_fitted.convert().coef

        a = round(a, 3)
        b = round(b, 3)
        c = round(c, 3)
        d = round(d, 3)
        print(str(a) + " * x^3 + " + str(b) + " * x^2 + " + str(c) + " * x + " + str(d) + " = y")

        plt.clf()
        plt.title("Voltage vs time")
        plt.plot(voltage_vs_time_x, voltage_vs_time_y, linewidth=3, c="b")
        for x_val in voltage_vs_time_x:
            y_val = a * x_val * x_val * x_val + b * x_val * x_val + c * x_val + d
            plt.scatter(x_val, y_val, c="r")
        plt.show()
        plt.clf()
    else:
        print("Can't fit polynomial")
except Exception as e:
    print(str(e))