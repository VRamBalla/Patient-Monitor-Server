#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 23:28:21 2022

@author: david
"""
import logging
import numpy as np
import math as m


def read_data(filename, path=''):
    '''Read a csv file containing ECG data and return a list with data points

    This function read a single csv file containing ECG data. The first column
    of the csv should be time in minutes and the second column in the csv file
    should be voltage in mV. The function will read the file row by row and
    return a nested list with each row in the csv file as the list element.

    Args:
        path (string): Relative path of the data file, default value is none
        filename (string): Strings containg file name

    Returns:
        datapoints (list): Nested list containing each line of the file
        file_path (string): Relative path and the file name for checking
    '''
    import csv
    logging.info("Start analysing {}".format(filename))
    datapoints = []
    if path == '':
        file_path = filename
    else:
        file_path = path + '/' + filename
    with open(file_path, 'r') as f:
        read = csv.reader(f)
        for row in read:
            datapoints.append(row)
    return datapoints, file_path


def convert_data(datapoints):
    '''Filter abberant datapoints, convert data into float, and find voltage
       extremes

    This function converts numeric strings in ECG data into float. If the
    function encounters non-numeric strings or missing data, it will remove
    them from the data. This function also finds the extreme voltage value and
    checks if the voltage is within the normal range.

    Args:
        datapoints (list): List containing ECG data point strings

    Returns:
        checked_data (list): List containing normal ECG data point numbers
        extreme (tuple): A tuple containing the minimum and maximum of the
        voltage
    '''
    checked_data = []
    outside_normal = False
    V_1stnumeric = True
    for index in range(0, len(datapoints)):
        try:
            V = float(datapoints[index][1])
            if m.isnan(V):
                logging.error("Data missing at {}".format(index))
                continue
            else:
                if abs(V) > 300 and outside_normal is False:
                    logging.warning("Voltage exceeds normal range (-300 ~ 300 "
                                    "mV)")
                    outside_normal = True
            if V_1stnumeric:
                maxV, minV = V, V
                V_1stnumeric = False
            else:
                if V > maxV:
                    maxV = V
                if V < minV:
                    minV = V

            T = float(datapoints[index][0])
            if m.isnan(T):
                logging.error("Data missing at {}".format(index))
                continue
            else:
                checked_data.append([T, V])
        except ValueError:
            logging.error("Data missing at {}".format(index))
            continue
    extreme = (minV, maxV)
    logging.info("Adding voltage extremes to the analysis result")
    return checked_data, extreme


def split_data_and_duration(checked_data):
    '''Split the checked data into time and voltage

    This function splits the checked data point list into a list of time and
    a list of voltage, and calculate the duration of the ECG strip

    Args:
        checked_data (list): Nested list where each element is a datapoint

    Returns:
        time (list): Time in seconds
        voltage (list): Voltage in mV
        duration (float): Duration of the ECG strip
    '''
    time, voltage = [], []
    for i in range(0, len(checked_data)):
        time.append(checked_data[i][0])
        voltage.append(checked_data[i][1])
    duration = time[-1] - time[0]
    logging.info("Adding duration to the analysis result")
    return time, voltage, duration


def running_mean(y, duration, window_size):
    '''Calculate the running average of voltage

    This function is a simplified version of the 1D uniform filter using the
    'reflect' mode. It calculates the running avaerage of the voltage signal
    based on the window size.

    Args:
        y (list): 1d sample data list
        duration (float): Duration of the sample time
        window_size (float): Time frame in second for calculating running
        average

    Returns:
        run_mean (1d numpy array): Running average for each point of the
        data

    Example:
        ```running_mean([12, -9, -6, 0, 1, 5], 6, 4)```
        First, the function calculates the size for obtaining running average,
        which is 6/6*4 = 4 in this case.
        Then, the function expand the input list by "reflect" mode to:
        w = [-9, 12, 12, -9, -6, 0, 1, 5, 5]
        The running average for each point in the input list will be obtained
        by:
        run_mean[i] = (w[i] + w[i+1] + w[i+2] + w[i+3])/4
        For example, run_mean[1] = (12+12-9-6)/4 = 2.25

    Reference:
        https://stackoverflow.com/questions/55207719/cant-understand-the-worki
        ng-of-uniform-filter1d-function-imported-from-scipy
    '''
    tmp = np.asarray(y)
    frequency = len(y)/duration
    size = int(frequency * window_size)
    if size > 2 * len(y):
        logging.error("Fail to calculate the running mean")
        raise ValueError("Window size can not exceed twice of the data "
                         "duration")
    if size == 0:
        logging.error("Fail to calculate the running mean")
        raise ValueError("window_size can not be 0")
    elif size == 1:
        logging.warning("Invalid running average calculation when size is 1")
        run_mean = tmp
    elif size == 2:
        working_data = np.insert(tmp, 0, tmp[0])
        run_mean = (working_data[:-1] + working_data[1:])/2
    elif size % 2 != 0:
        head = tmp[m.floor(size/2):0:-1]
        tail = tmp[-2:-m.floor(size/2)-2:-1]
        working_data = np.concatenate((head, tmp, tail))
        run_mean = np.zeros(tmp.size)
        for i in range(m.floor(size/2), tmp.size + m.floor(size/2)):
            run_mean[i-m.floor(size/2)] = np.sum(working_data[
                     i - m.floor(size/2):i + m.floor(size/2) + 1])/size
    elif size % 2 == 0:
        num_add = int(size/2)  # the result of size/2 is a float!
        head = tmp[num_add-1::-1]
        tail = tmp[-1:-num_add:-1]
        working_data = np.concatenate((head, tmp, tail))
        run_mean = np.zeros(tmp.size)
        for i in range(num_add, tmp.size+num_add):
            run_mean[i-num_add] = np.sum(working_data[i-num_add:
                                         i+num_add])/size
    return run_mean


def detect_peak(voltage, duration, window_size, offset_P):
    '''Detect peaks in the ECG

    This function detects peak groups by comparing each voltage value with its
    running mean. If the voltage is greater than its running mean, the voltage
    belongs to a peak group.

    Args:
        voltage (list): A list containing all the voltage value in mV
        duration (float): Duration of the ECG
        window_size (float): Time frame in second for calculating running
        average
        offset_P (float): Offset factor for adjusting the running mean

    Returns:
        peaks (list): A list containing the index of the peaks in the data

    Reference:
        heartpy package:
        https://github.com/paulvangentcom/heartrate_analysis_python/tree/master
        /heartpy
        https://python-heart-rate-analysis-toolkit.readthedocs.io/en/latest/in
        dex.html
    '''
    run_mean = running_mean(voltage, duration, window_size)
    if np.mean(run_mean) == 0:
        offset = 0.1 * offset_P  # 0.1 is an arbitrary value
    else:
        offset = np.mean(run_mean) * offset_P
    run_mean = run_mean + abs(offset)
    peak_index = np.where(voltage > run_mean)[0]
    if len(peak_index) <= 2:
        peaks = []
        return peaks
    peakY = np.asarray(voltage)[peak_index]
    peak_L_edge = np.concatenate((np.array([0]),
                                  np.where(np.diff(peak_index) > 1)[0] + 1,
                                  np.array([len(peak_index)])))
    peaks = []
    for i in range(0, len(peak_L_edge)-1):
        one_peak = peakY[peak_L_edge[i]:peak_L_edge[i+1]]
        tip_index = np.argmax(one_peak) + peak_L_edge[i]
        peaks.append(peak_index[tip_index])
    return peaks


def fit_peak(voltage, duration, window_size=0.75):
    '''Find the R peak in the peak list

    This function uses a series of predefined value to adjust the running
    average and calculate the standard deviation between successive differences
    (SDSD). The best fit of the offset factor is determined by the minimum
    SDSD. Finally, the function returns a R peak list with the best offset
    factor and reasonable interval.
    When the data quality is poor, the function may fail to acquire R peak list
    with reasonable interval. In this case, the function will simply seek the
    offset factor that gives the smallest SDSD.

    Args:
        voltage (list): A list containing all the voltage value in mV
        duration (float): Duration of the ECG
        window_size (float): Time frame in second for calculating running
        average, default value is 0.75 s.

    Returns:
        R_peaks (list): List of R peak index in the data
        offset[min_index] (float): Optimized offset factor (for testing)

    Reference:
        heartpy package:
        https://github.com/paulvangentcom/heartrate_analysis_python/tree/master
        /heartpy
        https://python-heart-rate-analysis-toolkit.readthedocs.io/en/latest/in
        dex.html
    '''
    offset = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
              1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.75, 2, 2.5, 2.75, 3, 3.5, 4]
    sdsd = []
    upbound = len(voltage)*1.6/duration
    # Set upper bound of the peak interval as 1.6s
    lowbound = len(voltage)*0.24/duration
    # set lower bound of the peak interval as 0.24 s based on the refractory
    # period of the cardio muscle.
    for i in range(0, len(offset)):
        peaks = detect_peak(voltage, duration, window_size, offset[i])
        if peaks is None or len(peaks) < 2:
            sdsd.append(float('inf'))
            continue
        distance = np.diff(np.asarray(peaks))
        if np.mean(distance) > upbound or np.mean(distance) < lowbound:
            sdsd.append(float('nan'))
            continue
        sdsd.append(np.std(distance))

    try:
        min_index = argmin(np.asarray(sdsd))
    except ValueError:
        logging.warning("Signal is too noisy, readjusting offset factor")
        for i in range(0, len(offset)):
            peaks = detect_peak(voltage, duration, window_size, offset[i])
            if peaks is None or len(peaks) < 2:
                sdsd.append(float('inf'))
                continue
            interval = np.diff(np.asarray(peaks))
            sdsd.append(np.std(interval))
        min_index = np.argmin(np.asarray(sdsd))
    R_peaks = detect_peak(voltage, duration, window_size, offset[min_index])
    logging.info("Raw R peak indexes obtained by offset factor {}".format(
                  offset[min_index]))
    return R_peaks, offset[min_index]


def argmin(nparray):
    '''Find the index of the smallest element in a numpy array

    This function finds the index of the smallest element in a numpy array with
    nan, inf, and numbers.
    If the function encounters an all-nan array, it will raise valuerror.
    If the array only contains nan and inf, the function returns the index of
    the last nan element in the array. The reason for this is that we prefer to
    obtain multiple peaks in the peak list instead of one single peak or no
    peak, and we want to filter out as much noise signal as possible.
    For arrays with a mixture of nan, inf, and numbers,the function will ignore
    the nan and inf.

    Args:
        nparray (array): 1d numpy array with nan, inf and/or numbers

    Returns:
        min_index (integer): Index of the smallest element in the array
    '''
    nan_num, inf_num, nan_index = 0, 0, 0
    for i in range(0, nparray.size):
        if m.isnan(nparray[i]):
            nan_num += 1
            nan_index = i
        if m.isinf(nparray[i]):
            inf_num += 1

    if nan_num == nparray.size:
        raise ValueError('All-nan array encountered')
    elif nan_num + inf_num == nparray.size:
        min_index = nan_index
    else:
        min_index = np.nanargmin(nparray)
    return min_index


def analyse_peak(voltage, time, duration, R_peaks):
    '''Filter peak signal and find the bpm

    This function filters the peak signal by checking each peak-to-peak
    interval. It only accepts peaks with reasonable interval. For high frequecy
    noisy signal, it tries to filter out the peaks with low voltage values
    before checking peak-to-peak interval. Finally, the function obtains the
    number of beats, bpm, and the beat timepoints with the corrected peaks.

    Args:
        voltage (list): A list containing all the voltage value in mV
        time (list): A list containing corresponding timepoints in s
        duration (float): Duration of the ECG
        R_peaks (list): List of R peaks index in the data

    Returns:
        num_beats (float): Number of beats in float numbers
        bpm (float): Heart rate in beats per minute
        beats (list): List of timepoints when the beat occurs

    Notes:
        This function assumes that the peak signal is always stronger than
        noise, so the function may fail to filter out the peak if the signal
        is too noisy.
    '''
    if len(R_peaks) < 2:
        logging.error("Too few peaks to analyse")
        num_beats, bpm, beats = 0, 0, [float('nan')]
        return num_beats, bpm, beats

    peak_interval = np.diff(np.asarray(R_peaks))
    T = np.asarray(time)
    R = np.asarray(R_peaks)
    upbound = len(voltage)*1.6/duration
    # Set upper bound of the peak interval as 1.6s
    lowbound = len(voltage)*0.24/duration
    # set lower bound of the peak interval as 0.24 s based on the refractory
    # period of the cardio muscle.
    flag = False
    if np.mean(peak_interval) < lowbound:
        flag = True
        V = np.asarray(voltage)
        factor = 0.3
        peaky = V[R_peaks]
        run_mean = running_mean(peaky, peaky.size, 4)
        while np.mean(peak_interval) < lowbound:
            if np.mean(run_mean) == 0:
                offset = 0.1*factor  # 0.1 is an arbitrary value
            else:
                offset = abs(np.mean(run_mean))*factor
            run_mean = run_mean - offset
            filtered = np.where(peaky > run_mean)[0]
            if filtered.size < 2:
                logging.error("Fail to analyse the signal due to strong noise")
                num_beats, bpm, beats = 0, 0, [float('nan')]
                return num_beats, bpm, beats
            peak_interval = np.diff(R[filtered])
            factor -= 0.04

    tmp = []
    for i in range(0, peak_interval.size):
        if lowbound <= peak_interval[i] <= upbound:
            tmp.append(i)
    tmp = np.asarray(tmp)
    normal = np.concatenate((tmp, np.array([tmp[-1] + 1])))
    num_beats = normal.size
    bpm = round(60*len(voltage)/(np.mean(peak_interval[tmp])*duration), 1)
    if flag:
        filtered_x = R[filtered]
        beats = T[filtered_x[normal]].tolist()
    else:
        beats = T[R[normal]].tolist()
    logging.info("Analysis completed successfully. Adding the number of beats,"
                 " bpm, and beat index into the analysis result")
    return num_beats, bpm, beats


def remove_suffix(filename):
    '''Remove the suffix of a file name

    This function removes the suffix (jpg, csv, etc.) of a given file name. It
    can handle file name containing extra dots.

    Args:
        filename (string): File name

    Returns:
        fname (string): File name string without suffix
    '''
    tmp = filename.split('.')[: -1]
    fname = ".".join(tmp)
    return fname


def output(filename, metrics, path='Analysis'):
    '''Save the analysis result in a JSON file

    Save the analysis result in the dictionary into a JSON file in designated
    folder. If the path is empty, the function will save the JSON file in the
    active working directory (Usually in the folder where you run this script).

    Args:
        filename (string): ECG data file name, including the filename extension
        metrics (dictionary): ECG analysis result in the format of
            {
                "duration": <ECG strip length as a float>,
                "voltage_extremes": [<min voltage float>, <max voltage float>],
                "num_beats": <number of detected beats as an int>,
                "mean_hr_bpm": <heart rate as a float>,
                "beats": [<beat 1 time point as a float>, ...]
            }
        path (string): Place to save the analysis result. The default is
            "Analysis"

    Returns:
        file_path (string): The relative path of the JSON file (for testing)
    '''
    import json
    import os

    fname = remove_suffix(filename)
    if path == '':
        file_path = fname + '.json'
    else:
        if not os.path.exists(path):
            os.mkdir(path)
        file_path = path + '/' + fname + '.json'
    with open(file_path, 'w') as write_f:
        json.dump(metrics, write_f)
    logging.info("save the result in {}".format(file_path))
    return file_path


def main_ECG_process(filename, path, path_output='Analysis'):
    '''Main function for ECG processing

    This function collects ECG data and save the analysis result in the
    designated folder. It can be called in other scripts for analysis purpose.

    Args:
        filename (string): ECG dataset file name
        path (string): The folder where the ECG dataset file is stored
        path_output (string): Folder to save the analysis result.
            The default is 'Analysis'.

    Returns:
        time (list): Time points in seconds
        voltage (list): Voltage in mV
        metrics (dictionary): Analysis result in the format of
            {
                "duration": <ECG strip length as a float>,
                "voltage_extremes": [<min voltage float>, <max voltage float>],
                "num_beats": <number of detected beats as an int>,
                "mean_hr_bpm": <heart rate as a float>,
                "beats": [<beat 1 time point as a float>, ...]
            }
        filepath (string): The path of the analysis json file

    '''
    logging.basicConfig(filename="ecg_log.log", level=logging.INFO)
    datapoints, _ = read_data(filename, path)
    # Take datapoints from the return
    metrics = {}
    checked_data, metrics['voltage_extremes'] = convert_data(datapoints)
    time, voltage, metrics["duration"] = split_data_and_duration(checked_data)

    R_peaks, _ = fit_peak(voltage, metrics['duration'])
    metrics['num_beats'], metrics['mean_hr_bpm'],\
        metrics['beats'] = analyse_peak(voltage, time, metrics['duration'],
                                        R_peaks)
    filepath = output(filename, metrics, path_output)
    return time, voltage, metrics, filepath


if __name__ == "__main__":
    main_ECG_process("test.csv", "")
