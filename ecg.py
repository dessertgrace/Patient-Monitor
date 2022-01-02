import logging
import numpy as np
import os
import math
import scipy
from scipy import signal
import matplotlib.pyplot as plt
import json


def input_data(file):
    logging.info("Analysis of ECG trace")
    with open(os.path.join("test_data", file), 'r') as f:
        pairs = np.genfromtxt(f, delimiter=",")
    times = []
    voltages = []
    for r, row in enumerate(pairs):
        times.append(row[0])
        voltages.append(row[1])
    return times, voltages


def remove_non_numbers(times, voltages, filename):
    times2 = []
    voltages2 = []
    for t, v in zip(times, voltages):
        if not math.isnan(float(t)) and not math.isnan(float(v)):
            times2.append(float(t))
            voltages2.append(float(v))
        else:
            logging.error("Missing entry, or NaN in {}".format(filename))
    # print(len(times2))
    # print(len(voltages2))
    return times2, voltages2


def above_three_hundred(voltages2, filename):
    counts = 0
    for voltage in voltages2:
        if abs(voltage) > 300:
            counts = counts + 1
            if counts > 1:
                break
            else:
                logging.warning("Voltage in {} exceeds normal"
                                " range".format(filename))
    return voltages2


def calc_duration(times2):
    duration = max(times2) - min(times2)
    logging.info("Duration: {}".format(duration))
    return duration


def calc_extremes(voltages2):
    voltage_extremes = ()
    voltage_extremes = list(voltage_extremes)
    max_voltage = max(voltages2)
    min_voltage = min(voltages2)
    voltage_extremes.append(min_voltage)
    voltage_extremes.append(max_voltage)
    voltage_extremes = tuple(voltage_extremes)
    logging.info("Voltage Extremes: {}".format(voltage_extremes))
    return voltage_extremes


def sampling_rate(times2):
    samp_rate = len(times2) / max(times2)
    return samp_rate


def filtering(samp_rate, voltages2):
    Wn = [(1 / (samp_rate / 2)), (50 / (samp_rate / 2))]
    b, a = scipy.signal.butter(3, Wn, 'band')
    filtered = scipy.signal.filtfilt(b, a, voltages2)
    return filtered


def peak_detection(filtered, times2):
    beats = []
    peaks, _ = scipy.signal.find_peaks(filtered,
                                       height=max(filtered) * 0.35,
                                       distance=100)
    plt.clf()
    plt.plot(filtered)
    plt.plot(peaks, filtered[peaks], "x")
    # plt.show()
    num_beats = len(peaks)
    for p, t in zip(peaks, times2):
        beats.append(times2[p])
    mean_hr_bpm = num_beats / (max(times2) - min(times2)) * 60
    logging.info("Number of beats: {}".format(num_beats))
    logging.info("Times of beats: {}".format(beats))
    logging.info("Mean HR (bpm): {}".format(mean_hr_bpm))
    # print(beats)
    # print(mean_hr_bpm)
    return num_beats, beats, mean_hr_bpm


def make_dictionary(duration, voltage_extremes, num_beats,
                    mean_hr_bpm, beats, csvname):
    metrics = {"duration": duration, "voltage_extremes":
               voltage_extremes, "num_beats": num_beats,
               "mean_hr_bpm": mean_hr_bpm, "beats": beats}
    filename = csvname.strip(".csv") + ".json"
    out_file = open(filename, "w")
    json.dump(metrics, out_file)
    out_file.close()
    in_file = open(filename, "r")
    new_variable = json.load(in_file)
    logging.info("JSON filename: {}".format(filename))
    logging.info("Dictionary: {}".format(new_variable))
    return out_file


if __name__ == "__main__":
    logging.basicConfig(filename="ecg.log", filemode='w',
                        level=logging.INFO)
    times, voltages = input_data("test_data20.csv")
    times2, voltages2 = remove_non_numbers(times, voltages,
                                           "test_data20.csv")
    voltages2 = above_three_hundred(voltages2, "test_data20.csv")
    duration = calc_duration(times2)
    voltage_extremes = calc_extremes(voltages2)
    samp_rate = sampling_rate(times2)
    filtered = filtering(samp_rate, voltages2)
    num_beats, beats, mean_hr_bpm = peak_detection(filtered, times2)
    make_dictionary(duration, voltage_extremes, num_beats,
                    mean_hr_bpm, beats, "test_data20.csv")
