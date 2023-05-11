import base64
import io
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from idlelib.tooltip import Hovertip
from PIL import Image, ImageTk
import requests
from datetime import datetime
from matplotlib import image as mpimg
import os

url = 'http://vcm-29744.vm.duke.edu:5000'


def sort_history_dict(history_dict):
    """Sort the input history_dict by the timestamp keys

    This function will sort the history_dict by the datetime key
    such that the latest record will be the last one of the new output dict

    Args:
        history_dict (dict): a dict in the format of {timestamp_str: int or
        str} depending on the specific input history_dict

    Returns:
        sorted_date_time_dict_out (dict): the sorted version of input
        history_dict by the timestamp keys. It's still in the format of {
        timestamp_str: int or str} depending on the specific input
        history_dict. The most recent record will be
        the last data pair in the dict
    """
    date_time_dict = {}
    for date_time_str, data in history_dict.items():
        date_time_dict[datetime.strptime(date_time_str, '%Y-%m-%d '
                                                        '%H:%M:%S')] = \
            data

    sorted_date_time_dict = dict(sorted(date_time_dict.items()))  # All the
    # keys in this dict will be datetime object

    sorted_date_time_dict_out = {}
    for date_time_obj, data in sorted_date_time_dict.items():
        sorted_date_time_dict_out[date_time_obj.strftime('%Y-%m-%d '
                                                         '%H:%M:%S')] = \
            data
    # Now all the keys in sorted_date_time_dict_out are str from the
    # corresponding datetime object following the format of "%Y-%m-%d %H:%M:%S"
    return sorted_date_time_dict_out


def latest_value_in_history_dict(history_dict):
    """Obtained the latest value in a dict by the timsetamp key

    This function sort key-value pairs in history_dict by the timestamp keys
    such that the latest pair is the last pair in the dict. Then it obtains
    that latest value.

    Args: history_dict (dict): a dictionary in the format of {timestamp_str:
    int or str} depending on the specific history_dict Returns: latest_value
    (int or str): the value in history_dict that has the latest
    timestamp_str. Specific type depends on the specific input history_dict
    """
    sorted_history_dict = sort_history_dict(history_dict)
    latest_value = list(sorted_history_dict.values())[-1]
    return latest_value


def latest_timestamp_in_history_dict(history_dict):
    """Obtained the latest timestamp in a dict

    This function sort key-value pairs in history_dict by the timestamp keys
    such that the latest pair is the last pair in the dict. Then it obtains
    that latest timestamp.

    Args:
        history_dict (dict): a dictionary in the format of {timestamp_str:
        int or str} depending on the specific history_dict
    Returns:
        latest_timestamp (str): the latest timestmap in history_dict
    """
    sorted_history_dict = sort_history_dict(history_dict)
    latest_timestamp = list(sorted_history_dict.keys())[-1]
    return latest_timestamp


def main_window():
    """Defines main window of the GUI

    The function creates requests patient information from mongodb
    database. For each patient, it creates widgets to show patient name,
    medical record number, and the latest heart rate. At the end of each
    patient's information, there is an ECG button which opens a new window.

    Returns:
        None.
    """
    root = tk.Tk()
    root.title("Patient ECG Monitor GUI")

    def openNewWindow(pat):
        """Defines new window of the GUI

        The function creates opens a new window. It is available for
        every patient. In the new window, the latest ECG is displayed,
        a combobox showing all the heart rates of the patient alongwith
        its timestamp, and a view button next to it.

        Returns:
            None.
        """
        newWindow = Toplevel(root)
        newWindow.title("ECG Display")

        def close_cmd():
            """ Defines close command of the new window

            The function acts as a command function to destroy the new window
            when the close button is pressed.

            Returns:
                None.
            """
            newWindow.destroy()

        Button(newWindow, text="Close", command=close_cmd).grid(column=7,
                                                                row=0)

        def auto_update_nw():
            """ Auto updates new window

            The function retrieves the specific patient's information from the
            database and updates the new window every 30 seconds.

            Returns:
                None.
            """
            patient = get_patient_data(pat['medical_record_number'])
            generator_nw(patient)
            root.after(30000, auto_update_nw)

        def generator_nw(pat):
            """Worker function of new window

            The function receives specific patient's information
            dictionary from the root window. It displays latest
            ECG information, a combobox showing the heart rate history
            of the patient alongwith timestamps, and calls the view_cmd
            function to display the selected ECG from the combobox.

            Args:
                pat (dict):{
            medical_record_number: int,
            patient_name: str,
            heart_rate_history: {timestmap_str: int},
            ecg_image_history: {timestmap_str: b64_str},
            medical_filename_history: {timestmap_str: filename_str},
            medical_image_history: {timestmap_str: b64_str}}

            Returns:
                None.
            """

            def view_cmd():
                """Displays selected ECG

                The function receives a particular heart rate from the
                combobox and displays the ECG corresponding to the heart
                rate.

                Returns:
                    None.
                """
                h_hist = hr_hist.get()
                timestamp = h_hist[1:20]

                img_str = pat['ecg_image_history'].get(timestamp)
                image_bytes2 = base64.b64decode(img_str)
                new2_filename = 'ecg2.jpg'
                with open(new2_filename, "wb") as out_file:
                    out_file.write(image_bytes2)
                pil_image = Image.open(new2_filename)
                pil_image = pil_image.resize((300, 300))

                tk_image = ImageTk.PhotoImage(pil_image)
                image_label = Label(newWindow, image=tk_image)
                image_label.image = tk_image
                image_label.grid(column=5, row=3)

            if len(pat['ecg_image_history']) == 0:
                Label(newWindow, text="-")
            else:
                sor_ecg = sort_history_dict(pat['ecg_image_history'])
                lat_ecg = latest_value_in_history_dict(sor_ecg)

                image_bytes = base64.b64decode(lat_ecg)
                new_filename = 'ecg.jpg'
                with open(new_filename, "wb") as out_file:
                    out_file.write(image_bytes)
                pil_image = Image.open(new_filename)
                pil_image = pil_image.resize((300, 300))
                tk_image = ImageTk.PhotoImage(pil_image)
                image_label = Label(newWindow, image=tk_image)
                image_label.image = tk_image
                image_label.grid(column=0, row=3)
                Label(newWindow, text="Latest ECG").grid(column=0, row=0)

                hr_hist_list = list(pat['heart_rate_history'].items())
                hr_hist = tk.StringVar()
                hr_hist_combo = Combobox(newWindow,
                                         textvariable=hr_hist,
                                         width=25)
                hr_hist_combo.grid(column=5, row=0)
                hr_hist_combo["values"] = hr_hist_list

                Button(newWindow,
                       text="View",
                       command=view_cmd).grid(column=6,
                                              row=0)

        auto_update_nw()

    def get_all_med_number():
        """Obtain all the medical record number from the database

        This function uses the route '/api/monitor/all_med_number' and based
        on the sttaus code, either to return a list of all the medical
        record number if the database has least 1 record or an empty list if
        the database is empty

        Returns:
            all_med_number_list (list of int or str): if the server is
        well-connected, a list of all the
        medical record number if the database has least 1 record or [] if the
        database is empty.
        """
        r = requests.get(url + '/api/monitor/all_med_number')
        if r.status_code == 200:
            all_med_number_list = r.json()
        else:
            all_med_number_list = []
        return all_med_number_list

    def get_patient_data(record_number):
        """Obtain a patient's info dict by the given record_number

        This function uses the route
        /api/monitor/patient_info/<record_number> to obtain a patient's info
        dict by the given record number. If the returned patient info dict
        is empty, that means the database doesn't have record for the given
        record_number

        Args:
            record_number (int): patient record number

        Returns:
            patient_info_dict (dict of dict): if the server connection has
        no issues, {} if the database has no record for the given
        record_number or {
        medical_record_number: int,
        patient_name: str,
        heart_rate_history: {timestmap_str: int},
        ecg_image_history: {timestmap_str: b64_str},
        medical_filename_history: {timestmap_str: filename_str},
        medical_image_history: {timestmap_str: b64_str}}
        """
        r = requests.get(
            url + '/api/monitor/patient_info/{}'.format(record_number))
        if r.status_code == 200:
            patient_info_dict = r.json()
        else:
            patient_info_dict = {}
        return patient_info_dict

    def auto_update():
        """ Auto updates root window

        The function calls the get_all_med_number function to get the
        latest list of all the patients on db every 30 seconds.

        Returns:
            None.
        """
        all_med_list = get_all_med_number()
        if len(all_med_list) != 0:
            generator(all_med_list)
        root.after(30000, auto_update)

    def generator(all_med_list):
        """Worker function of root window

        The function receives the list of medical numbers for each
        patient. Retrieves information for each patient and creates labels for
        each patient's name, medical record number, latest heart rate and
        a ECG button to display ECG information.

        Args:
            all_med_list (list): list containing all patient medical
            record numbers (int)

        Returns:
            None.
        """
        l1 = Label(root, text=" Medical Record No. ").grid(column=0,
                                                           row=0,
                                                           columnspan=2)
        l2 = Label(root, text=" Patient Name ").grid(column=5,
                                                     row=0,
                                                     columnspan=2)
        l3 = Label(root, text=" Latest Heart Rate ").grid(column=10,
                                                          row=0,
                                                          columnspan=2)
        for i, rec_no in enumerate(all_med_list):
            pat = get_patient_data(rec_no)
            if len(pat['heart_rate_history']) == 0:
                lat_hr = "no hr"
            else:
                sorted_hr = sort_history_dict(pat['heart_rate_history'])
                pat['heart_rate_history'] = sorted_hr
                lat_hr = latest_value_in_history_dict(sorted_hr)
            if pat['patient_name'] is None:
                pat['patient_name'] = "<no name>"

            nam_l = Label(root, text=pat['patient_name'])
            nam_l.grid(column=5, row=i+1, columnspan=2)

            rec_l = Label(root, text=pat['medical_record_number'])
            rec_l.grid(column=0, row=i+1, columnspan=2)

            hr_l = Label(root, text=lat_hr)
            hr_l.grid(column=10, row=i+1, columnspan=2)

            but = Button(root, text="ECG",
                         command=lambda pat=pat: openNewWindow(pat))
            but.grid(column=15, row=i+1, columnspan=2)

    auto_update()
    root.mainloop()


if __name__ == '__main__':
    main_window()
