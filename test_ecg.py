import math
from math import nan
import pytest
from ecg import input_data
from ecg import remove_non_numbers
from ecg import sampling_rate
from ecg import filtering
from ecg import calc_duration
from ecg import above_three_hundred
from ecg import calc_extremes
from ecg import peak_detection
from ecg import make_dictionary
import numpy as np
from math import sqrt
import testfixtures
from testfixtures import LogCapture

input = "test_data_RL_1.csv"
output1 = [0.0, 0.003, 0.006, 0.009, 0.012, 0.015, 0.018, 0.021, 0.024, 0.027]
output2 = [-0.14, 0.15, 1.2, 0.8, 0.3, 0.2, 0.13, 0.64, -0.2, 3.0]
input2 = "test_data_RL_2.csv"
output19 = [0.0, 0.003, 0.006, 0.009, 0.012, 0.015, 0.018, 0.021, 0.024, 0.027]
output20 = [0.0, -0.3, 0.6, 0.3, 300, 45, 0.6, 0.77, 0, 35]


@pytest.mark.parametrize("input, expected1, expected2", [
    (input, output1, output2),
    (input2, output19, output20)])
def test_input_data(input, expected1, expected2):
    from ecg import input_data
    answer1, answer2 = input_data(input)
    assert answer1 == expected1
    assert answer2 == expected2


times1 = [0.0, 0.003, 0.006, 0.009, 0.012, 0.015, 0.018, 0.021, 0.024, 0.027]
voltages1 = [nan, nan, 0.6, 0.3, 300.0, 45.0, 0.6, 0.77, 0.0, 35.0]
filename1 = "test_data_RL_2.csv"
output3 = [0.006, 0.009, 0.012, 0.015, 0.018, 0.021, 0.024, 0.027]
output4 = [0.6, 0.3, 300.0, 45.0, 0.6, 0.77, 0.0, 35.0]


@pytest.mark.parametrize("times, voltages, filename, expected3, expected4", [
    (times1, voltages1, filename1, output3, output4)])
def test_remove_non_numbers(times, voltages, filename, expected3, expected4):
    from ecg import remove_non_numbers
    answer1, answer2 = remove_non_numbers(times, voltages, filename)
    assert answer1 == expected3
    assert answer2 == expected4


times3 = [0.0, 0.003, 0.006, 0.009, 0.012, 0.015, 0.018, 0.021, 0.024, 0.027]
times4 = [4, 5, 6, 7, 8, 9, 10]


@pytest.mark.parametrize("times2, expected", [
    (times3, 0.027),
    (times4, 6)])
def test_calc_duration(times2, expected):
    from ecg import calc_duration
    answer = calc_duration(times2)
    assert answer == expected


voltages2 = [0.0, 0.003, 0.006, 0.009, 0.012,
             0.015, 0.018, 0.021, 0.024, 0.027]
voltages3 = [0.0]
output5 = (0.0, 0.027)
output6 = (0.0, 0.0)


@pytest.mark.parametrize("voltages2, expected5", [
    (voltages2, output5),
    (voltages3, output6)])
def test_calc_extremes(voltages2, expected5):
    from ecg import calc_extremes
    answer = calc_extremes(voltages2)
    assert answer == expected5


times5 = [1, 2, 3, 4, 5, 6, 7]
output7 = 1


@pytest.mark.parametrize("times2, expected6", [
    (times5, output7)])
def test_sampling_rate(times2, expected6):
    from ecg import sampling_rate
    answer = sampling_rate(times2)
    assert answer == expected6


times6, voltages4 = input_data("test_data11.csv")
times7, voltages5 = remove_non_numbers(times6, voltages4,
                                       "test_data11.csv")
samp_rate1 = sampling_rate(times7)
filtered1 = filtering(samp_rate1, voltages5)
duration1 = calc_duration(times7)
output8 = 32
output9 = [0.544, 1.356, 2.228, 3.128, 3.969, 4.828,
           5.664, 6.508, 7.331, 8.222, 9.103, 9.939,
           10.794, 11.65, 12.481, 13.292, 14.167, 15.047,
           15.9, 16.786, 17.614, 18.433, 19.258, 20.167,
           21.047, 21.897, 22.761, 23.606, 24.447, 25.283,
           26.169, 27.031]
output10 = 32 / duration1 * 60
times8, voltages6 = input_data("test_data32.csv")
times9, voltages7 = remove_non_numbers(times8, voltages6,
                                       "test_data32.csv")
samp_rate2 = sampling_rate(times9)
filtered2 = filtering(samp_rate2, voltages6)
duration2 = calc_duration(times9)
output11 = 19
output12 = [0.043, 0.793, 1.543, 2.293, 3.043, 3.793,
            4.543, 5.293, 6.043, 6.793, 7.543, 8.293,
            9.043, 9.793, 10.543, 11.293, 12.043, 12.793,
            13.543]
output13 = 19 / duration2 * 60
times10, voltages8 = input_data("test_data20.csv")
times11, voltages9 = remove_non_numbers(times10, voltages8,
                                        "test_data32.csv")
samp_rate3 = sampling_rate(times11)
filtered3 = filtering(samp_rate3, voltages9)
duration3 = calc_duration(times11)
output14 = 19
output15 = [0.043, 0.793, 1.543, 2.293,
            3.043, 3.793, 4.543, 5.293,
            6.043, 6.793, 7.543, 8.293,
            9.043, 9.793, 10.543, 11.293,
            12.043, 12.793, 13.543]
output16 = 19 / duration3 * 60


@pytest.mark.parametrize("filtered, times2, expected1, expected2, expected3",
                         [(filtered1, times7, output8, output9,
                           output10),
                          (filtered2, times9, output11, output12,
                           output13),
                          (filtered3, times11, output14, output15,
                           output16)])
def test_peak_detection(filtered, times2, expected1, expected2, expected3):
    from ecg import peak_detection
    answer1, answer2, answer3 = peak_detection(filtered, times2)
    assert answer1 == expected1
    assert answer2 == expected2
    assert answer3 == expected3


def test_filtering():
    times12, voltages10 = input_data("test_data1.csv")
    times13, voltages11 = remove_non_numbers(times12, voltages10,
                                             "test_data1.csv")
    times14, voltages12 = input_data("filter_test_data.csv")
    times15, voltages13 = remove_non_numbers(times14, voltages12,
                                             "filter_test_data.csv")
    ms = 0
    for v, voltage in enumerate(voltages11):
        ms = ms + (voltages11[v]) ** 2
    ms = ms / len(voltages11)
    rms1 = sqrt(ms)
    filtered4 = filtering(len(times13) / max(times13), voltages11)
    ms2 = 0
    for f, filtered in enumerate(filtered4):
        ms2 = ms2 + (filtered4[f]) ** 2
    ms2 = ms2 / len(filtered4)
    rms2 = sqrt(ms2)
    ms3 = 0
    for v, voltage in enumerate(voltages13):
        ms3 = ms3 + (voltages13[v]) ** 2
    ms3 = ms3 / len(voltages13)
    rms3 = sqrt(ms3)
    filtered5 = filtering(len(times15) / max(times15), voltages13)
    ms4 = 0
    for f, filtered in enumerate(filtered5):
        ms4 = ms4 + (filtered5[f]) ** 2
    ms4 = ms4 / len(filtered5)
    rms4 = sqrt(ms4)
    assert rms1 * 0.5 > rms2
    assert abs(rms3 - rms4) < 0.5


def test_logging_errors_and_info():
    with LogCapture() as log_c:
        file = "test_data20.csv"
        times, voltages = input_data("test_data20.csv")
        remove_non_numbers(times, voltages, file)
    log_c.check(("root", "INFO", "Analysis of ECG trace"),
                ("root", "ERROR", "Missing entry, or NaN in test_data20.csv"),
                ("root", "ERROR", "Missing entry, or NaN in test_data20.csv"))


def test_logging_warnings():
    with LogCapture() as log_c:
        file = "test_data32.csv"
        times, voltages = input_data("test_data32.csv")
        times2, voltages2 = remove_non_numbers(times, voltages, file)
        above_three_hundred(voltages2, file)
    log_c.check(("root", "INFO", "Analysis of ECG trace"),
                ("root", "WARNING", "Voltage in"
                                    " test_data32.csv exceeds normal range"))
