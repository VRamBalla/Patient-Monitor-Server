#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 15:32:18 2022

@author: david
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, UnidentifiedImageError
import base64
import csv
import math as m
import matplotlib.pyplot as plt
import numpy as np
from ecg_analysis import main_ECG_process, remove_suffix
import requests


def img_resize(image):
    '''Resize the image to fit the GUI

    This function resize the image to fit the GUI. The default width is 150 px.

    Args:
        image (PIL image): Medical image opened by the user

    Returns:
        image (PIL image): Resized image
    '''
    x, y = image.size
    newx = 150
    newy = int(y * newx / x)
    image = image.resize((newx, newy))
    return image


def check_ecg_file(ecg_filename):
    '''Check the file for ECG analysis

    This function checks if the file chosen by the user is a qualified ECG
    data file. It rejects the non-csv files and csv files with a column number
    other than 2

    Args:
        ecg_filename (string): Path of the ECG data file

    Returns:
        check (boolean): True if the file is qualified, otherwise the value is
        false.
        path (string): The relative folder path where the data file is stored
        file (string): Name of the ECG data file

    '''
    fname = ecg_filename.split('.')
    check = False
    path, file = None, None
    if fname[-1] != 'csv':
        return check, path, file
    try:
        with open(ecg_filename, 'r') as f:
            read = csv.reader(f)  # csv method won't ignore blank lines, so
            T_prev = float("-inf")  # data files with blank lines are rejected
            datapoints = []
            for row in read:
                if len(row) != 2:
                    return check, path, file
                try:
                    T, V = float(row[0]), float(row[1])
                    if m.isnan(T) or m.isnan(V):
                        continue
                    if T <= T_prev:
                        return check, path, file
                    T_prev = T
                    datapoints.append([T, V])
                except ValueError:
                    continue
    except IOError:
        return check, path, file

    if len(datapoints) < 2:
        return check, path, file
    else:
        duration = datapoints[-1][0] - datapoints[0][0]
        f = len(datapoints)/duration
        if duration < 0.38 or f < 10:
            return check, path, file
    # split the ECG_filename into file path and file name
    check = True
    path_tmp = ecg_filename.split("/")
    if len(path_tmp) == 1:
        path = ''
    elif len(path_tmp) == 2 and path_tmp[0] == '':
        path = '/'  # Handle the case when the file is stored at '/'
    else:
        path = '/'.join(path_tmp[:-1])
    file = path_tmp[-1]
    return check, path, file


def visualization(time, voltage, metrics, file_name):
    '''Plot the ECG data

    This function plots the ECG data and the accepted peaks. The figure is
    saved in the same folder as the analysis result with the same file name as
    the ECG data

    Args:
        time (list): ECG timepoint in seconds
        voltage (list): Voltage in mV
        metrics (dictionary): ECG analysis result in the format of
            {
                "duration": <ECG strip length as a float>,
                "voltage_extremes": [<min voltage float>, <max voltage float>],
                "num_beats": <number of detected beats as an int>,
                "mean_hr_bpm": <heart rate as a float>,
                "beats": [<beat 1 time point as a float>, ...]
            }
        file_name (string): File path of the ECG analysis result

    Returns:
        x (list): The index of beat time points
        lgnd (list): Legend in the plot
        fname (string): The file name the ECG plot
    '''
    plt.cla()
    V = np.asarray(voltage)
    plt.plot(time, voltage)
    if m.isnan(metrics['beats'][0]):
        lgnd = ["Signal"]
        x = None
        plt.legend(lgnd, bbox_to_anchor=(1, 1))
    else:
        x = []
        lgnd = ["Signal", "Accepted peaks"]
        for t in metrics['beats']:
            x.append(time.index(t))
        plt.plot(metrics['beats'], V[x], '.')
        plt.legend(lgnd, bbox_to_anchor=(1, 1))
    fname = remove_suffix(file_name)
    fname = fname + '.jpg'
    plt.savefig(fname, bbox_inches="tight")
    plt.close()
    return x, lgnd, fname


def img_2_b64(img_path):
    '''Convert an image to a base64 string

    This function converts the image to base64 string for uploading. The
    encoding is utf-8

    Args:
        img_path (string): Path of the image file.

    Returns:
        b64str (string): Base64 string of the image.

    '''
    with open(img_path, 'rb') as img:
        b64bytes = base64.b64encode(img.read())
    b64str = str(b64bytes, encoding="utf-8")
    return b64str


def validate_record(record):
    '''Check the record entry

    The record entry should only have spaces or numbers. This function checks
    if the record entry meets the requirements and remove all the spaces in the
    input.

    Args:
        record (string): Patient record number entry

    Returns:
        tag (string): Result of validation
        record_no_space (string): Patient record number without spaces

    '''
    record_no_space = ''
    if record.isspace() or record == '':
        tag = "Empty record"
        return tag, record_no_space
    else:
        for char in record:
            if char.isdigit():
                record_no_space = record_no_space + char
            elif char == ' ':
                continue
            else:
                tag = "Invalid record"
                record_no_space = ''
                return tag, record_no_space
        tag = 'pass'
        return tag, record_no_space


def validate_name(name):
    '''Validate the name input

    The name entry should only contain letters, spaces, or '.'. This function
    checks if the name input meets the requirements. If the name entry is empty
    or only has spaces, the function directly return without checking

    Args:
        name (string): Name entry

    Returns:
        tag (string): Validation result

    '''
    if name == '' or name.isspace():
        tag = 'Empty name'
    else:
        for char in name:
            if char.isalpha() is False:
                if char in [' ', '.']:
                    continue
                else:
                    tag = "Invalid name"
                    return tag
        tag = 'pass'
    return tag


def check_text_input(name, record):
    '''Check the patient name and record number

    This function checks if the patient name and record number meet the
    requirement and returns the check result

    Args:
        name (string): Name entry
        record (string): Patient record number entry

    Returns:
        tag (string): Check result
        record_no (string): Patient record number without spaces

    '''
    tag, record_no = validate_record(record)
    if tag != 'pass':
        return tag, record_no
    else:
        tag = validate_name(name)
        return tag, record_no


def upload_info(name, record, ecg_b64str, img_b64str, img_filename, hr,
                warn_sent="false"):
    '''Upload the patient information to the server

    This function put the patient information together into a dictionary with
    the format of:
        {
            "patient_record_no": <int> (mandatory)
            "patient_name": <str> (blank if not provide)
            "medical_img": <b64str> (blank if not provide)
            "img_filename": <str> (blank if not provide)
            "ECG_img": <b64str> (blank if not provide)
            "heart_rate": <str> (blank if not provide)
        }
    If the GUI could not connect to the server or receive the response from the
    server after 35 seconds, it returns the error message.

    Args:
        name (string): Patient name.
        record (integer): Patient record.
        ecg_b64str (string): Base64 string of ECG plots
        img_b64str (string): Base64 string of medical images
        img_filename(string): Medical image file name
        hr (string): Heart rate
        warn_sent (string): Indicate if the user wants to overwrite the old
        data. Defaults to "false", "true" if the user confirms overwriting

    Returns:
        interger: Status code from the server (For 111, this means network
                  error)
        string: Information from the server (For 111, this means network error)

    '''
    info = {}
    info["patient_record_no"] = record
    info["patient_name"] = name
    info["medical_img"] = img_b64str
    info["img_filename"] = img_filename
    info["ECG_img"] = ecg_b64str
    info["heart_rate"] = hr
    try:
        r = requests.post("http://vcm-29744.vm.duke.edu:5000/"
                          "patient_GUI/upload/" + warn_sent, json=info,
                          timeout=35)
    except (requests.ConnectionError, requests.exceptions.ReadTimeout):
        return 111, "Fail to connect to the server"
    return r.status_code, r.text


def main_window():
    '''Main window of the patient side GUI

    Define all the widgets in the GUI and their corresponding commands

    Returns:
        None.

    '''
    img_filename = ""
    ecg_plotname = ""
    hr = ""
    ecg_b64str = ""
    img_b64str = ""
    # These variables will be used in multiple functions

    def ecg_cmd():
        '''Command for ECG analysis

        This function checks if the ECG data file is valid. If it is valid, it
        will plot the ECG signal and give the heart rate. The plot will be
        converted to base64 string.

        Returns:
            None.

        '''
        nonlocal ecg_plotname, hr, ecg_b64str
        ecg_filename = filedialog.askopenfilename()
        if ecg_filename == '':
            return
        check, path, file = check_ecg_file(ecg_filename)
        if check is False:
            messagebox.showerror(message="Not an acceptable ECG data file.\n"
                                 "ECG data should be in a csv file with two "
                                 "columns. The first column should be time in"
                                 " seconds and the second column should be "
                                 "voltage in mV. The duration should be at "
                                 "least 0.38s and the sample frequency should"
                                 " be at least 10 Hz")
        else:
            time, voltage, metrics, filepath = main_ECG_process(file, path,
                                                                "ecg_analysis")
            _, _, ecg_plotname = visualization(time, voltage, metrics,
                                               filepath)
            # There is a way to use the plot without saving to disk by using
            # the in-memory file-like Bytesio class, but there is something
            # wrong when matplotlib/Bytesio works in the pytest scenario.
            #  Thus, this method is temporarily suspended.
            ecg_b64str = img_2_b64(ecg_plotname)
            ECG_plot = Image.open(ecg_plotname)
            ECG_plot = img_resize(ECG_plot)
            tk_ECG = ImageTk.PhotoImage(ECG_plot)
            ECG_label.configure(image=tk_ECG)
            ECG_label.image = tk_ECG
            hr = str(int(metrics["mean_hr_bpm"]))
            bpm.configure(text="Bpm: "+hr)
            bpm.text = "Bpm: " + hr
            ecg_plotname = ecg_plotname.split('/')[-1]

    def load_img():
        '''Load medical image

        This function loads the medical image by a dialouge. It raises error
        window if the user tries to open a file that is not an image. The image
        is then converted to base64 string.

        Returns:
            None.
        '''
        nonlocal img_filename, img_b64str
        img_name = filedialog.askopenfilename()
        if img_name == '':
            return
        img_filename = img_name.split('/')[-1]
        try:
            image = Image.open(img_name)
            image = img_resize(image)
            tk_img = ImageTk.PhotoImage(image)
            img_label.configure(image=tk_img)
            img_label.image = tk_img
            img_b64str = img_2_b64(img_name)
        except UnidentifiedImageError:
            messagebox.showerror(message="Not an image file")

    def upload_cmd():
        '''Command for uplaoding information

        This function checks the patient information before update and show the
        corresponding error or message window. If any input is invalid, an
        error window will be prompted. Otherwise, a window summarizing
        information to be uploaded will show to allow user to double check.
        If the name provided by the user is already exist in the database, the
        function will ask if the user wants to overwrite the name.

        Returns:
            None.

        '''
        nonlocal ecg_b64str, img_b64str, img_filename
        name = name_entry.get()
        record = record_Entry.get()
        # Checking section
        tag, record = check_text_input(name, record)
        if tag == "Empty record":
            status.configure(text="Please provide a patient record number",
                             foreground='red')
            status.text = "Please provide a patient record number"
            messagebox.showerror(message="Please provide a patient record "
                                 "number")
        elif tag == "Invalid record":
            status.configure(text="Patient record number should only contain "
                             "numbers", foreground='red')
            status.text = "Patient record number should only contain numbers"
            messagebox.showerror(message="Patient record number should only "
                                 "contain numbers")
        elif tag == "Invalid name":
            status.configure(text="Name should only contain letters",
                             foreground='red')
            status.text = "Name should only contain letters"
            messagebox.showerror(message="Name should only contain letters")
        else:  # Check pass
            if tag == "Empty name":
                name = ""
            record = int(record)
            ans = messagebox.askokcancel(message="The following information "
                                         " will be uploaded: \n"
                                         "Patient name: {}\n"
                                         "Patient record: {}\n"
                                         "ECG file: {}\n"
                                         "Bpm: {}\n"
                                         "Medical image: {}".
                                         format(name, record, ecg_plotname, hr,
                                                img_filename))
            if ans:  # User confirm uploading
                status.configure(text="Uploading...", foreground='black')
                status.text = "Uploading..."
                root.update()
                code, msg = upload_info(name, record, ecg_b64str,
                                        img_b64str, img_filename, hr)
                if code == 200:  # Patient name overwrite warning
                    ans1 = messagebox.askokcancel(message="The name you "
                                                  "provide for patient {} "
                                                  "is different from the one "
                                                  "in the record. Do you want "
                                                  "to overwrite the existing "
                                                  "name?".format(record))
                    if ans1:
                        status.configure(text="Uploading...",
                                         foreground='black')
                        status.text = "Uploading..."
                        root.update()
                        code, msg = upload_info(name, record, ecg_b64str,
                                                img_b64str, img_filename, hr,
                                                "true")
                        if code != 201:
                            messagebox.showerror(message="{}: {}".format(code,
                                                                         msg))
                            status.configure(text=msg, foreground='red')
                            status.text = msg
                        else:
                            status.configure(text=msg, foreground='black')
                            status.text = msg
                elif code == 201:  # Patient information updated
                    status.configure(text=msg, foreground='black')
                    status.text = msg
                else:
                    messagebox.showerror(message="{}: {}".format(code, msg))
                    status.configure(text=msg, foreground='red')
                    status.text = msg

    def clear_cmd():
        nonlocal img_filename, img_b64str, ecg_b64str, ecg_plotname, hr
        ans = messagebox.askokcancel(message="Are you sure to clear all "
                                     "information?")
        if ans:
            name_box.delete(first=0, last=len(name_entry.get()))
            record_box.delete(first=0, last=len(record_Entry.get()))
            img_label.configure(image="")
            img_filename = ""
            img_b64str = ""
            ECG_label.configure(image="")
            ecg_plotname = ""
            ecg_b64str = ""
            hr = ""
            bpm.configure(text="")
            status.configure(text="Please input the patient information you"
                             " want to upload", foreground="black")
            status.text = "Please input the patient information you want to "
            "upload"

    def cancel_cmd():
        '''Close the GUI

        This command completly shut down the GUI

        Returns:
            None.

        '''
        ans = messagebox.askokcancel(message="Leave the GUI? All information"
                                     "you input will be lost")
        if ans:
            root.destroy()

    root = tk.Tk()
    root.title("Patient side GUI")
    root.rowconfigure(1, minsize=50)
    # First row
    ttk.Label(root, text="Patient information").grid(column=0, row=0)
    # Second row
    ttk.Button(root, text="Load image", command=load_img).grid(column=2, row=1)
    ttk.Button(root, text="ECG analysis", command=ecg_cmd).\
        grid(column=3, row=1)
    # Third row
    ttk.Label(root, text="Name").grid(column=0, row=2)
    name_entry = tk.StringVar()
    name_box = ttk.Entry(root, textvariable=name_entry)
    name_box.grid(column=1, row=2)
    img_label = ttk.Label(root)
    img_label.grid(column=2, row=2, rowspan=2)
    ECG_label = ttk.Label(root)
    ECG_label.grid(column=3, row=2, rowspan=2)
    # Fourth row
    ttk.Label(root, text="Patient record No.").grid(column=0, row=3)
    record_Entry = tk.StringVar()
    record_box = ttk.Entry(root, textvariable=record_Entry)
    record_box.grid(column=1, row=3)
    # Fifth row
    bpm = ttk.Label(root)
    bpm.grid(column=3, row=4)
    # Sixth row
    ttk.Button(root, text="Upload", command=upload_cmd).grid(column=1, row=5)
    ttk.Button(root, text="Clear", command=clear_cmd).grid(column=2, row=5)
    ttk.Button(root, text="Cancel", command=cancel_cmd).grid(column=3, row=5)
    # Bottom row
    status = ttk.Label(root, text="Please input the patient information you"
                       " want to upload")
    status.grid(column=0, row=6, columnspan=4, sticky="W")

    root.mainloop()


if __name__ == "__main__":
    main_window()
