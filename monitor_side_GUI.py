import base64
import io
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from idlelib.tooltip import Hovertip
from PIL import Image, ImageTk
import requests
from datetime import datetime

from matplotlib import image as mpimg

# url = 'http://127.0.0.1:5000'  # Used to connect to server. Later change to
# remote server VM
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


def organize_patient_info_for_GUI(patient_info_dict):
    """Organize the sub dict inside of patient_info_dict so it's better for
    the GUI to use

    This function will go through all the data field from the raw
    patient_info_dict obtained from the server. If a dict datafield is {} or
    a str datafield is None, it fills in '(No data yet)' for those fileds.
    For all the other fields that have dict, it will sort those dict such
    that the latest key-value pair is on the last of the dictionary

    Args:
        patient_info_dict (dict): the raw patient_info_dict that can
    contain data field as {} if the field is a dict or None if the field is
    a str. Other dict datafields that are non-empty are in the order they
    are in the database. They should be in the format as {
    medical_record_number: int, patient_name: str, heart_rate_history: {
    timestmap_str: int}, ecg_image_history: {timestmap_str: b64_str},
    medical_filename_history: {timestmap_str: filename_str},
    medical_image_history: {timestmap_str: b64_str}}

    Returns:
        patient_info_dict (dict): the same patient_info_dict but with any
        empty datafield filled up as '(No data yet)' and all the non-empty
        dict data fields to be sorted
    """
    if patient_info_dict == {}:
        return
    else:
        for key in patient_info_dict.keys():
            if patient_info_dict[key] == {} or patient_info_dict[key] is \
                    None:  # The patient name field can be None if empty
                patient_info_dict[key] = '(No data yet)'
            else:
                if key != 'patient_name' and key != 'medical_record_number':
                    # These 2 fields are not dictionaries so they cannot be
                    # sorted
                    patient_info_dict[key] = sort_history_dict(
                        patient_info_dict[key])
        return patient_info_dict


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


def convert_b64_str_to_ndarray(b64_string):
    """Converts a b64_string into a ndarray

    This function converts a base64 string into a ndarray with image data,
    so it can be used later to display in GUI

    Args:
         b64_string (str): string variable containing the image bytes
         encoded as a base64 string

    Returns:
        img_ndarray (ndarray):variable containing an ndarray with image data
    """
    image_bytes = base64.b64decode(b64_string)
    image_buf = io.BytesIO(image_bytes)
    img_ndarray = mpimg.imread(image_buf, format='JPG')
    return img_ndarray


def resize_image(image_pil):
    """Resize an image_pil, so it fits into the GUI

    This function obtains the original image's size and resize it to have
    the new x as 150 proportionally so the new image can fit in the GUI

    Args:
        image_pil (PIL image): the imput image to be resized

    Returns:
        out_image_pil (PIL image): the new PIL image that now is
        proportionally resized to have the new_x as 150
    """
    # This need a unit test
    x, y = image_pil.size
    new_x = 150
    new_y = int(y * new_x / x)
    out_image_pil = image_pil.resize((new_x, new_y))
    return out_image_pil


def b64_str_to_img_download(b64_str, file_direct):
    """Save a b64_str into a file

    This function will save the b64_str into an image file locally by the
    given file directory

    Args:
        b64_str (str): the base64 string that contains the image data
        file_direct (str): the file directory to use to save the image

    Returns:
        0 or 1 (int): indicators of whether the code was successfully
        operated. 0 if sucessful and 1 if not
    """
    image_bytes = base64.b64decode(b64_str)
    if file_direct:  # User selected file
        with open(file_direct, 'wb') as save_file:
            save_file.write(image_bytes)
        return 0
    else:  # User cancels the file browser window
        return 1


def judge_int_str(input_str):
    """Judge whether input_str is a string that contains only numeric
    characters

    This functions uses a try-except block to judge whether input_str
    contains only numeric characters

    Args:
        input_str (str): a string that can contain only numeric characters
        or mixed with some other types of characters

    Returns:
        True or False (bool): bool indicator for the judgement. True if
    the string contains only number characters and False if the string
    contains some other kinds of characters
    """
    try:
        int(input_str)
    except (Exception,):
        return False
    else:
        return True


def main_window():
    """ Defines main window of the GUI

    The function creates the widgets and layout for the main window of the
    monitoring GUI. This GUI contains 4 tabs (tab0-3) and each tab has its
    own sub functions to create widgets on that tab. Some widgets have
    "command" functions linked to them, and those command functions can be
    found as "sub-functions" of this function as well

    These sub-functions should only do three things:
        1. Get information from the GUI
        2. Call separate, modular, testable functions to do the work
        3. Update the GUI as necessary based on response for functions in
        step 2.

    Returns:
        0 (int): indicator for successful code operation
    """

    def main_root_tab_setup():
        """Create the major root-tabs notebook window

        This function lays the basic of the root window and the 4-tab
        notebook so the whole root window is more organized and the user
        will be guided through by whether a tab is open or locked based on
        the user's responses or the condition judgements by the auto update
        functions

        Returns:
            root (window): the root window that contains everything
            tab_control (notebook): the notebook that contains all the tabs
            tab_0 (frame or tab): tab for Database status and all its widgets
            tab_1 (frame or tab): tab for Basic patient information and all
            its widgets
            tab_2 (frame or tab): tab for ECG image display and all its
            widgets
            tab_3 (frame or tab): tab for Medical image display and all its
            widgets
        """
        # Define the main window
        root = tk.Tk()

        # Basic root configuration
        root.title('BLH Monitoring Station (Checking for database status)')
        # root.geometry('600x600')

        # Use a tab system to make the GUI more organized and intuitive
        tab_control = ttk.Notebook(root)

        # Configure the font of tabs
        tab_style = ttk.Style()
        tab_style.configure('TNotebook.Tab', font=('Arial', 18, 'bold'))

        # Configure the font of widgets
        widget_style = ttk.Style()
        widget_style.configure('.', font=('Arial', 12, 'bold'))

        # Set up the tab system
        tab_0 = ttk.Frame(tab_control)
        tab_1 = ttk.Frame(tab_control)
        tab_2 = ttk.Frame(tab_control)
        tab_3 = ttk.Frame(tab_control)

        for tab, tab_name, tab_init_state in zip(
                [tab_0, tab_1, tab_2, tab_3],
                ['Database status', 'Basic patient information', 'ECG images',
                 'Medical images'],
                ['normal', 'disabled', 'disabled', 'disabled']
        ):
            tab.configure(padding=(5, 5), relief='sunken')
            tab_control.add(tab)
            tab_control.add(tab, text=tab_name)
            tab_control.tab(tab, state=tab_init_state)

        tab_control.pack(
            fill="both")  # Pack the tab control to make the tabs visible
        return root, tab_control, tab_0, tab_1, tab_2, tab_3

    def combobox_clean_widget_only(combobox):
        """Return the user selection from combobox and clean it

        This function will use the get() method first to obtain the user
        selection from a combobox and then clean it up. Doing so will clean
        up the previous residual option to avoid any confusion from user

        Args:
            combobox (widget): the input combobox where user made a selection

        Returns:
            selection (str): the returned user selection from the input
            combobox
        """
        # This method exists is to get the user's selection before clear up the
        # combobox where that selection was made
        selection = combobox.get()
        combobox.set('')
        return selection

    def tab_0_setup():
        """Set up tab 0 Database status

        This function sets up the tab 0 for checking on the database status
        in a more organized way with default message saying '(Checking for
        database status)...' in yellow background

        Returns:
            database_status_label (widget): the label that will indicate
            whether the database that the server is connecting to is empty
            or not
        """
        # ****** Tab 0: Database status ******
        database_status_label = ttk.Label(
            tab_0,
            text='(Checking for database status)...',
            background='yellow',
        )
        database_status_label.grid(column=0, row=0)
        return database_status_label

    def tab_1_setup():
        """Set up tab 1 Basic patient information

        This function sets up the tab 1 for displaying basic patient
        information in a more organized way with several labels to display
        obtained data,
        1 OK button, 1 combobox, and 1 Cancel Button

        Returns:
            tab_1_ok_button (widget): button to click to send in the
            selected record number
            tab_1_cancel_button (widget): button to click to have an option
            to quite the monitoring GUI
            tab_1_record_number_combo (widget): combobox to select record
            number
            tab_1_selected_record_number_label (widget): label to show the
            user selected record number
            tab_1_patient_name_label (widget): label to show the
            corresponding patient name
            tab_1_latest_heart_rate_label (widget): label to show the
            corresponding latest heart rate
            tab_1_latest_heart_rate_time_label (widget): label to show the
            corresponding timestamp of the latest heart rate
        """

        # ****** Tab 1: Basic patient information ******

        def tab_1_sect_1_setup():
            """Set up tab 1 Basic patient information section 1 Select
            patient medical record number

            This function sets up the tab 1 for displaying basic patient
            information section 1 Select
            patient medical record number
            in a more organized way with 1 OK button, 1 Cancel button and 1
            combobox for record number selection

            Returns:
                tab_1_ok_button (widget): button to click to send in the
                selected record number
                tab_1_cancel_button (widget): button to click to have an option
                to quite the monitoring GUI
                record_number_combo (widget): combobox to select record
                number

            """
            # ************ Widget group 1: Select patient medical record number
            # ************
            ttk.Label(
                tab_1,
                text='Section 1: Select patient medical record number:'
            ).grid(column=0, row=0, sticky='E', pady=2)

            tab_1_ok_button = ttk.Button(tab_1, text='OK',
                                         command=tab_1_ok_cmd, state='normal')
            tab_1_ok_button.grid(column=2, row=0, pady=2)

            tab_1_cancel_button = ttk.Button(tab_1, text='Cancel',
                                             command=tab_1_cancel_cmd,
                                             state='normal')
            tab_1_cancel_button.grid(column=3, row=0, pady=2)

            record_number = tk.StringVar()
            record_number.set('')
            record_number_combo = ttk.Combobox(
                tab_1,
                textvariable=record_number,
                width=70,
                values=get_all_med_number(),
                state='readonly'
            )
            record_number_combo.grid(column=1, row=0, pady=2)
            record_number_combo.set('')  # Set the default to blank
            return tab_1_ok_button, tab_1_cancel_button, record_number_combo

        def tab_1_sect_1_half_setup():
            """Set up a separator and the prompt between section 1 and 2 on
            tab 1

            This function sets up separator and the prompt between section 1
            and 2 on tab 1 in a more organized way

            Return:
                None
            """
            # ************ Widget group 1.5: section label
            # ************
            ttk.Separator(tab_1, orient='horizontal').grid(column=0, row=1,
                                                           columnspan=4,
                                                           sticky='we')
            ttk.Label(
                tab_1,
                text='Section 2: Corresponding patient information retrieved '
                     'from database'
            ).grid(column=0, row=2, columnspan=4, pady=2)

        def tab_1_sect_2_setup():
            """Set up tab 1 Basic patient information section 2 display the
            obtained patient name, record number, the latest heart rate and its
            timestamp

            This function sets up the 1 Basic patient information section 2
            display the obtained patient name, record number, the latest
            heart rate and its timestamp in a more organized way with
            several labels to display the obtained data

            Returns:
                selected_record_number_label (widget): label to show the
                user selected record number
                patient_name_label (widget): label to show the
                corresponding patient name
                latest_heart_rate_label (widget): label to show the
                corresponding latest heart rate
                latest_heart_rate_time_label (widget): label to show the
                corresponding timestamp of the latest heart rate
            """
            # ************ Widget group 2: Display selected record number
            # ************
            ttk.Label(tab_1,
                      text='Medical record number you '
                           'selected:').grid(column=0, row=3, sticky='E',
                                             pady=2)

            selected_record_number_label = ttk.Label(tab_1,
                                                     text='(Empty)',
                                                     background='yellow')
            selected_record_number_label.grid(column=1, row=3, pady=2)
            Hovertip(selected_record_number_label,
                     'Select a record numer to see verified record number '
                     'selection here')

            # ************ Widget group 3: Display patient name ************
            ttk.Label(tab_1, text='Corresponding '
                                  'patient name:').grid(column=0, row=4,
                                                        sticky='E', pady=2)

            patient_name_label = ttk.Label(tab_1, text='(Empty)',
                                           background='yellow')
            patient_name_label.grid(column=1, row=4, pady=2)
            Hovertip(patient_name_label,
                     'Select a record numer to see patient name here')

            # ************ Widget group 4: Display latest heart rate
            # ************
            ttk.Label(tab_1, text='Latest '
                                  'heart '
                                  'rate ('
                                  'bpm):').grid(column=0, row=5, sticky='E',
                                                pady=2)

            latest_heart_rate_label = ttk.Label(tab_1, text='(Empty)',
                                                background='yellow')
            latest_heart_rate_label.grid(column=1, row=5, pady=2)
            Hovertip(latest_heart_rate_label,
                     'Select a record numer to see latest heart rate here')

            # ************ Widget group 5: Display latest heart rate time
            # ************
            ttk.Label(tab_1,
                      text='Timestamp for latest '
                           'heart '
                           'rate:').grid(column=0, row=6, sticky='E', pady=2)

            latest_heart_rate_time_label = ttk.Label(
                tab_1,
                text='(Empty)',
                background='yellow')
            latest_heart_rate_time_label.grid(column=1, row=6, pady=2)
            Hovertip(latest_heart_rate_time_label,
                     'Select a record numer to see '
                     'latest heart rate timestamp here')

            ttk.Label(tab_1, text='*Yellow (Empty) means the GUI is waiting '
                                  'for user selection and white (No data '
                                  'yet) means the patient has no '
                                  'record in that data field.\n*Tabs for ECG '
                                  'Images and Medical Images will be '
                                  'activated by clicking OK on this tab with '
                                  'a valid medical record number '
                                  'selection.', font=('Arial', 12)
                      ).grid(
                column=0, row=7, pady=2, columnspan=4, sticky='w')
            return \
                selected_record_number_label, patient_name_label, \
                latest_heart_rate_label, latest_heart_rate_time_label

        tab_1_ok_button, tab_1_cancel_button, \
            tab_1_record_number_combo = tab_1_sect_1_setup()

        tab_1_sect_1_half_setup()

        tab_1_selected_record_number_label, tab_1_patient_name_label, \
            tab_1_latest_heart_rate_label, \
            tab_1_latest_heart_rate_time_label = tab_1_sect_2_setup()

        return \
            tab_1_ok_button, tab_1_cancel_button, \
            tab_1_record_number_combo, tab_1_selected_record_number_label, \
            tab_1_patient_name_label, tab_1_latest_heart_rate_label, \
            tab_1_latest_heart_rate_time_label

    def tab_2_setup():
        """Set up tab 2 ECG images

        This function sets up the tab 2 for displaying ECG images in a more
        organized way with several labels to display obtained data,
        1 OK button, 1 combobox to select ECG to display, 1 combobox to
        select which ECG to download and 1 Download button to download the
        selected ECG

        Returns: tab_2_ecg_latest_img_label (widget): label to display the
        latest ECG tab_2_ecg_latest_timestamp_label (widget): label to
        display the timestamp for the latest ECG tab_2_ecg_history_combo (
        widget): combobox of the whole ECG history tab_2_ecg_display_button
        (widget): button to click to display the selected ECG
        tab_2_ecg_selected_img_label (widget): label to display the selected
        ECG tab_2_ecg_selected_timestamp_label (widget): label to display
        the timestamp for the selected ECG tab_2_ecg_download_combo (
        widget): combobox to select which side (latest or selected) of the
        ECG to download tab_2_ecg_download_button (widget): button to click
        to start the download process
        """

        # ****** Tab 2: ECG images ******
        def tab_2_sect_1_setup():
            """Set up tab 2 ECG images section 1 display the latest ECG

            This function sets up the tab 2 ECG images section 1 display the
            latest ECG in a more organized way with 2 labels to display the
            latest ECG image and its timestamp

            Returns:
                ecg_latest_img_label (widget): label to display the latest ECG
                ecg_latest_timestamp_label (widget): label to display the
                timestamp for the latest ECG
            """
            # ************ Widget group 1: latest ECG
            # image
            # ************
            ttk.Label(tab_2,
                      text='Section 1: Below is '
                           'the '
                           'latest '
                           'ECG image in records').grid(column=0, row=0,
                                                        pady=2, columnspan=2)
            ttk.Label(tab_2, text='Image: ').grid(column=0, row=1)
            ttk.Label(tab_2, text='Timstamp: ').grid(column=0, row=2)

            ecg_latest_img_label = ttk.Label(tab_2, text='(Empty)',
                                             image='',
                                             background='yellow')
            ecg_latest_img_label.grid(column=1, row=1, pady=2)

            ecg_latest_timestamp_label = ttk.Label(tab_2, text='(Empty)',
                                                   background='yellow')
            ecg_latest_timestamp_label.grid(column=1, row=2, pady=2)
            return ecg_latest_img_label, ecg_latest_timestamp_label

        def tab_2_sect_2_setup():
            """Set up tab 2 ECG images section 2 display the selected ECG

            This function sets up the tab 2 ECG images section 2 display the
            selected ECG in a more organized way with 1 combobox to select
            ECG to display, 1 OK button as confirmation, and 2 labels to
            display the selected ECG and its timestamp

            Returns:
                ecg_history_combo (widget): combobox of the whole ECG
            history
            ecg_display_button (widget): button to click to display
            the selected ECG
            ecg_selected_img_label (widget): label to display the
            selected ECG
            ecg_selected_timestamp_label (widget): label to display the
            timestamp for the selected ECG
            """
            # ************ Widget group 2: display historical ECG image
            # ************
            ttk.Separator(tab_2, orient='vertical').grid(column=2, row=0,
                                                         rowspan=3,
                                                         sticky='ns')
            # sticky is
            # necessary to make the separator visible to human eyes
            ttk.Label(tab_2,
                      text='Section 2: Select historical ECG '
                           'image in records by timestamp to '
                           'display '
                           'below: ').grid(
                column=3, row=0,
                pady=2,
                columnspan=2)

            ecg_selected_timestamp_var = tk.StringVar()
            ecg_history_combo = ttk.Combobox(
                tab_2,
                textvariable=ecg_selected_timestamp_var)
            ecg_history_combo.grid(column=5, row=0, pady=2)
            ecg_history_combo.state(['readonly'])
            ecg_history_combo.set('')

            ecg_display_button = ttk.Button(tab_2, text='OK',
                                            command=tab_2_ok_cmd,
                                            state='disabled')
            ecg_display_button.grid(column=6, row=0, pady=2)

            ttk.Label(tab_2, text='Image: ').grid(column=3, row=1)
            ttk.Label(tab_2, text='Timstamp: ').grid(column=3, row=2)

            ecg_selected_img_label = ttk.Label(tab_2, text='(Empty)',
                                               image='',
                                               background='yellow')
            ecg_selected_img_label.grid(column=3, row=1, pady=2, columnspan=3)

            ecg_selected_timestamp_label = ttk.Label(tab_2,
                                                     text='(Empty)',
                                                     background='yellow')
            ecg_selected_timestamp_label.grid(column=3, row=2, pady=2,
                                              columnspan=3)
            return \
                ecg_history_combo, ecg_display_button, \
                ecg_selected_img_label, ecg_selected_timestamp_label

        def tab_2_set_3_setup():
            """Set up tab 2 ECG images section 3 download an ECG

            This function sets up the tab 2 ECG images section 3 download an
            ECG in a more organized way with 1 combobox to select which ECG
            to download and 1 Download button to downloda that selected ECG

            Returns: ecg_download_combo (widget): combobox to select which
            side (latest or selected) of the ECG to download
            ecg_download_button (widget): button to click to start the
            download process
            """
            # ************ Widget group 3: download image ************
            ttk.Separator(tab_2, orient='horizontal').grid(column=0, row=3,
                                                           columnspan=6,
                                                           sticky='we')

            ttk.Label(tab_2,
                      text='Section 3: Select to '
                           'download ECG '
                           'image file(s) locally: '
                           '').grid(column=0,
                                    row=4,
                                    columnspan=5,
                                    pady=2)

            download_ecg_img = tk.StringVar()
            ecg_download_combo = ttk.Combobox(tab_2,
                                              textvariable=download_ecg_img)
            ecg_download_combo.grid(column=5, row=4, pady=2)
            ecg_download_combo['values'] = ['Latest ECG image (Left)',
                                            'Historical ECG image (Right)']
            ecg_download_combo['width'] = 30
            ecg_download_combo.state(['disabled'])
            ecg_download_combo.set('')

            ecg_download_button = ttk.Button(tab_2,
                                             text='Download',
                                             command=tab_2_download_cmd,
                                             state='disabled')
            ecg_download_button.grid(column=6, row=4, pady=2, sticky='w')
            Hovertip(ecg_download_button,
                     'Click Display button to display the desired ECG to '
                     'activate '
                     'Download '
                     'button')

            ttk.Label(tab_2, text='*Yellow (Empty) means the GUI is waiting '
                                  'for user selection and white (No data '
                                  'yet) means the patient has no '
                                  'record in that data field.\n*Download '
                                  'button will be activated by a click '
                                  'on the OK button on this tab.',
                      font=('Arial',
                            12)
                      ).grid(
                column=0, row=5, pady=2,
                columnspan=6, sticky='w'
            )

            return ecg_download_combo, ecg_download_button

        tab_2_ecg_latest_img_label, \
            tab_2_ecg_latest_timestamp_label = tab_2_sect_1_setup()

        tab_2_ecg_history_combo, tab_2_ecg_display_button, \
            tab_2_ecg_selected_img_label, \
            tab_2_ecg_selected_timestamp_label = tab_2_sect_2_setup()

        tab_2_ecg_download_combo, \
            tab_2_ecg_download_button = tab_2_set_3_setup()

        return \
            tab_2_ecg_latest_img_label, tab_2_ecg_latest_timestamp_label, \
            tab_2_ecg_history_combo, tab_2_ecg_display_button, \
            tab_2_ecg_selected_img_label, \
            tab_2_ecg_selected_timestamp_label, tab_2_ecg_download_combo, \
            tab_2_ecg_download_button

    def tab_3_setup():
        """Set up tab 3 Medical images

        This function sets up the tab 3 for displaying medical images in a
        more organized way with several labels to display the data,
        1 combobox for medical image selection, 1 OK button for confirmation
        and 1 Dowload button to download the selected medical image

        Returns:
            tab_3_med_history_combo (widget): combobox for selecting the
            medical image history
            tab_3_med_display_button (widget): button to click to display
            the selected medical image
            tab_3_med_selected_img_label (widget): label to display the
            selected medical image
            tab_3_med_selected_filename_label (widget): label to display the
             filename of the selected medical image
            tab_3_med_selected_timestamp_label (widget): label to display
            the timestamp of the selected medical image
            tab_3_med_download_button (widget): button to click to start the
             download process for the selected medical image
        """

        # ****** Tab 3: Medical images ******

        def tab_3_sect_1_setup():
            """Set up tab 3 Medical images section 1 display a selected
            medical image

            This function sets up the tab 3 Medical images section 1 display
            a selected medical image in a more organized way

            Returns:
                med_history_combo (widget): combobox for selecting the
                medical image history
                med_display_button (widget): button to click to display
                the selected medical image
                med_selected_img_label (widget): label to display the
                selected medical image
                med_selected_filename_label (widget): label to display the
                 filename of the selected medical image
                med_selected_timestamp_label (widget): label to display
                the timestamp of the selected medical image
            """
            # ************ Widget group 1: display image ************
            ttk.Label(tab_3,
                      text='Section 1: Select medical '
                           'image in records to display '
                           'below: ').grid(column=0, row=0, pady=2,
                                           columnspan=2)

            med_selected_timestamp_var = tk.StringVar()
            med_history_combo = ttk.Combobox(
                tab_3,
                textvariable=med_selected_timestamp_var)
            med_history_combo.grid(column=2, row=0, pady=2)
            med_history_combo.state(['readonly'])
            med_history_combo.set('')

            med_display_button = ttk.Button(tab_3, text='OK',
                                            command=tab_3_ok_cmd)
            med_display_button.grid(column=3, row=0, pady=2)

            ttk.Label(tab_3, text='Image: ').grid(column=0, row=1, pady=2)
            med_selected_img_label = ttk.Label(tab_3, text='(Empty)',
                                               image='',
                                               background='yellow')
            med_selected_img_label.grid(column=1, row=1, pady=2)

            ttk.Label(tab_3, text='Filename: ').grid(column=0, row=2, pady=2)
            med_selected_filename_label = ttk.Label(tab_3,
                                                    text='(Empty)',
                                                    background='yellow')
            med_selected_filename_label.grid(column=1, row=2, pady=2)

            ttk.Label(tab_3, text='Timestamp: ').grid(column=0, row=3, pady=2)
            med_selected_timestamp_label = ttk.Label(tab_3,
                                                     text='(Empty)',
                                                     background='yellow')
            med_selected_timestamp_label.grid(column=1, row=3, pady=2)
            return \
                med_history_combo, med_display_button, \
                med_selected_img_label, med_selected_filename_label, \
                med_selected_timestamp_label

        def tab_3_sect_2_setup():
            """Set up tab 3 Medical images section 2 download a selected
            medical image

            This function sets up the tab 3 Medical images section 2
            download a selected medical image in a more organized way

            Returns:
                med_download_button (widget): button to click to start
            the download process for the selected medical image
            """

            # ************ Widget group 2: download image ************
            ttk.Separator(tab_3, orient='horizontal').grid(column=0, row=4,
                                                           columnspan=4,
                                                           sticky='we')

            ttk.Label(tab_3,
                      text='Section 2: Download current '
                           'medical image '
                           'file '
                           'locally: ').grid(column=0, row=5, columnspan=2,
                                             pady=2, sticky='e')

            med_download_button = ttk.Button(tab_3,
                                             text='Download',
                                             command=tab_3_download_cmd,
                                             state='disabled')
            med_download_button.grid(column=2, row=5, pady=2, columnspan=2,
                                     sticky='w')

            ttk.Label(tab_3, text='*Yellow (Empty) means the GUI is waiting '
                                  'for user selection and white (No data '
                                  'yet) means the patient has no '
                                  'record in that data field.\n*Download '
                                  'button will be activated by a click '
                                  'on the OK button on this tab.',
                      font=('Arial',
                            12)
                      ).grid(
                column=0, row=6, pady=2,
                columnspan=4, sticky='w'
            )
            return med_download_button

        tab_3_med_history_combo, tab_3_med_display_button, \
            tab_3_med_selected_img_label, tab_3_med_selected_filename_label, \
            tab_3_med_selected_timestamp_label = tab_3_sect_1_setup()

        tab_3_med_download_button = tab_3_sect_2_setup()

        return \
            tab_3_med_history_combo, tab_3_med_display_button, \
            tab_3_med_selected_img_label, \
            tab_3_med_selected_filename_label, \
            tab_3_med_selected_timestamp_label, tab_3_med_download_button

    def get_all_med_number():
        """Obtain all the medical record number from the database

        This function uses the route '/api/monitor/all_med_number' and based
        on the sttaus code, either to return a list of all the medical
        record number if the database has least 1 record or ['(Server
        database is empty. Have at least 1 patient entry to proceed.)'] if
        the database is empty

        Returns:
            all_med_number_list (list of int or str): if the server is
        well-connected, a list of all the
        medical record number if the database has least 1 record or ['(
        Server database is empty. Have at least 1 patient entry to
        proceed.)'] if the database is empty. If the server is not well
        conencted, it will be ['Server connection has problems']
        """
        # Professor mentioned that functions like this do not need unit test
        # functions since it simply obtains data from the server's database
        try:
            r = requests.get(url + '/api/monitor/all_med_number')
        except (Exception,):
            root.destroy()  # Terminate the GUI since the server connection
            # has issues
            return ['Server connection has problems']

        if r.status_code == 200:
            all_med_number_list = r.json()
        else:
            all_med_number_list = [
                '(Server database is empty. Have at least 1 patient entry to '
                'proceed.)']
        return all_med_number_list

    def get_patient_data(record_number):
        """Obtain a patient's info dict by the given record_number

        This function uses the route
        /api/monitor/patient_info/<record_number> to obtain a patient's info
        dict by the given record number. If the returned patient info dict
        is empty, that means the database doesn't have record for the given
        record_number

        Returns:
            patient_info_dict (dict of dict): if the server connection has
            no issues, {} if the database has no
            record for the given record_number or {
    medical_record_number: int, patient_name: str, heart_rate_history: {
    timestmap_str: int}, ecg_image_history: {timestmap_str: b64_str},
    medical_filename_history: {timestmap_str: filename_str},
    medical_image_history: {timestmap_str: b64_str}} if the corresponding
    patient info was found by the record_number. If the server connection
    has issues, it returns {{'status': 'Server connection has problems'}}
        """
        # Professor mentioned that functions like this do not need unit test
        # functions since it simply obtains data from the server's database
        try:
            r = requests.get(
                url + '/api/monitor/patient_info/{}'.format(record_number))
        except (Exception,):
            root.destroy()  # Terminate the GUI since the server connection
            # has issues
            return {{'status': 'Server connection has problems'}}

        if r.status_code == 200:
            patient_info_dict = r.json()
        else:
            patient_info_dict = {}
            messagebox.showwarning('Warning',
                                   'Patient information not found by the '
                                   'given medical record number.')

        return patient_info_dict

    def convert_ndarray_to_tk_image(img_ndarray):
        """Convert img_ndarray into a tk_image to display in the GUI

        This function converts the img_ndarray as a pil image, does a
        resize, and then convert that into a tk_image to display in the GUI

        Args:
            img_ndarray (ndarray): variable containing a ndarray with image
            data

        Returns:
            tk_image (TK image): variable containing an image to use with a
            Label widget
        """
        # Professor mentioned that no need to unit test this function since
        # tk_image is more on the GUI side.
        image_obj = Image.fromarray(img_ndarray)
        image_obj = resize_image(
            image_obj)  # Resize the image. Otherwise it is too
        # big to show in the GUI
        tk_image = ImageTk.PhotoImage(image_obj)
        return tk_image

    def tab_1_ok_button_click_and_auto_update_core(record_number_content):
        """Handler function for updating all the information on all the tabs

        After the user clicks on the OK button on tab 1 or when an auto
        update is triggered, it judges whether the record_number_content is
        empty. It gives a warning if the record_number_content is empty or
        updates all the tabs if not

        Args: record_number_content (int): the record_number that's unique
        for each patient in the database

        Returns:
            0 (int): indicator of success code operation
        """
        if record_number_content == '':  # This means the user has not
            # made a selection yet
            messagebox.showwarning('Warning', 'Select a patient medical '
                                              'record number in the '
                                              'dropdown menu first to '
                                              'see basic patient information '
                                              'and get access to ECG image '
                                              'tab and medical image tab.')
        else:
            patient_info_dict = get_patient_data(record_number_content)
            organized_patient_info_dict = organize_patient_info_for_GUI(
                patient_info_dict)

            core_update_tab_1(organized_patient_info_dict)
            core_update_tab_2(organized_patient_info_dict)
            core_update_tab_3(organized_patient_info_dict)

            # Only give accesses of tab_2 and tab_3 to the
            # user if a medical record number has been selected
            for tab in [tab_2, tab_3]:  # These are tab 2 and 3
                tab_control.tab(tab, state='normal')
        return 0

    def core_update_tab_1(organized_patient_info_dict):
        """Core function that updates tab 1 Nasic patient information

        This funciton is the real worker that updates all the fields on tab
        1 based on the given organized_patient_info_dict when either the OK
        button on tab 1 is clicked or the auto update is triggered. It will
        update the patient name, the latest heart rate, and its timestamp with
        some background color changing

        Args:
            organized_patient_info_dict (dict of dict): {
    medical_record_number: int, patient_name: str, heart_rate_history: {
    timestmap_str: int}, ecg_image_history: {timestmap_str: b64_str},
    medical_filename_history: {timestmap_str: filename_str},
    medical_image_history: {timestmap_str: b64_str}}

        Returns:
            None
        """
        # This function mainly updates widgets in tab 1 section 2

        # Obtain updated information
        patient_name = organized_patient_info_dict['patient_name']
        heart_rate_history = organized_patient_info_dict['heart_rate_history']

        # Update several widgets' background color
        for widget in [tab_1_selected_record_number_label,
                       tab_1_patient_name_label,
                       tab_1_latest_heart_rate_label,
                       tab_1_latest_heart_rate_time_label]:
            widget.configure(background='white')

        # Update several widgets' contents
        tab_1_selected_record_number_label.configure(
            text=organized_patient_info_dict['medical_record_number'])
        tab_1_patient_name_label.configure(text=patient_name)

        if heart_rate_history == '(No data yet)':
            latest_heart_rate = '(No data yet)'
            latest_heart_rate_timestamp = '(No data yet)'
        else:
            latest_heart_rate = latest_value_in_history_dict(
                organized_patient_info_dict['heart_rate_history'])
            latest_heart_rate_timestamp = latest_timestamp_in_history_dict(
                organized_patient_info_dict['heart_rate_history'])

        tab_1_latest_heart_rate_label.configure(text=latest_heart_rate)
        tab_1_latest_heart_rate_time_label.configure(
            text=latest_heart_rate_timestamp)

    def core_update_tab_2(organized_patient_info_dict):
        """Core function that updates tab 2 ECG images

        This funciton is the real worker that updates all the fields on tab
        2 based on the given organized_patient_info_dict when either the OK
        button on tab 1 is clicked or the auto update is triggered. It will
        update the latest ECG image and its timestamp with some background
        color changing. It will also update the combobox options on tab 2
        for all the possible ECG options

        Args:
            organized_patient_info_dict (dict of dict): {
    medical_record_number: int, patient_name: str, heart_rate_history: {
    timestmap_str: int}, ecg_image_history: {timestmap_str: b64_str},
    medical_filename_history: {timestmap_str: filename_str},
    medical_image_history: {timestmap_str: b64_str}}

        Returns:
            None
        """

        # Update the latest ECG
        # Update several widgets' background color
        ecg_image_history = organized_patient_info_dict['ecg_image_history']

        for widget in [tab_2_ecg_latest_img_label,
                       tab_2_ecg_latest_timestamp_label]:
            widget.configure(background='white')

        if ecg_image_history == '(No data yet)':
            latest_ecg = '(No data yet)'
            latest_ecg_img_tk = ''
            latest_ecg_timestamp = '(No data yet)'
            tab_2_ecg_latest_img_label.configure(image=latest_ecg_img_tk,
                                                 text=latest_ecg)
            tab_2_ecg_latest_img_label.image = latest_ecg_img_tk
        else:
            # Update several widgets' contents in tab 2 section 1
            latest_ecg_b64 = latest_value_in_history_dict(
                ecg_image_history)

            # Image conversion
            latest_ecg_ndarray = convert_b64_str_to_ndarray(
                latest_ecg_b64)
            latest_ecg_img_tk = convert_ndarray_to_tk_image(
                latest_ecg_ndarray)

            latest_ecg_timestamp = latest_timestamp_in_history_dict(
                ecg_image_history)

            tab_2_ecg_latest_img_label.configure(image=latest_ecg_img_tk)
            tab_2_ecg_latest_img_label.image = latest_ecg_img_tk

        tab_2_ecg_latest_timestamp_label.configure(
            text=latest_ecg_timestamp)

        # Update tab 2 section 2
        if ecg_image_history == '(No data yet)':
            tab_2_ecg_history_combo.set('(No data yet)')
            tab_2_ecg_history_combo.configure(values=[], state='disabled')
            tab_2_ecg_display_button.configure(state='disabled')
            tab_2_ecg_download_button.configure(state='disabled')
        else:
            if tab_2_ecg_history_combo.get() == '(No data yet)':
                tab_2_ecg_history_combo.set('')  # Clean the previous reisudal
                # text in the combobox

            tab_2_ecg_history_combo.configure(values=list(
                ecg_image_history.keys()),
                state='readonly')

            tab_2_ecg_display_button.configure(state='normal')
            # tab_2_ecg_download_button will be activated by the click on
            # the OK button on tab 2

    def core_update_tab_3(organized_patient_info_dict):
        """Core function that updates tab 3 Medical images

        This funciton is the real worker that updates all the fields on tab
        3 based on the given organized_patient_info_dict when either the OK
        button on tab 1 is clicked or the auto update is triggered. It will
        update the combobox on tab 3 for all the possible medical image
        options

        Args:
            organized_patient_info_dict (dict of dict): {
    medical_record_number: int, patient_name: str, heart_rate_history: {
    timestmap_str: int}, ecg_image_history: {timestmap_str: b64_str},
    medical_filename_history: {timestmap_str: filename_str},
    medical_image_history: {timestmap_str: b64_str}}

        Returns:
            None
        """

        # Update tab 3 section 1 for medical image selection
        medical_image_history = organized_patient_info_dict[
            'medical_image_history']

        if medical_image_history == '(No data yet)':
            tab_3_med_history_combo.set('(No data yet)')
            tab_3_med_history_combo.configure(values=[], state='disabled')
            tab_3_med_display_button.configure(state='disabled')
            tab_3_med_download_button.configure(state='disabled')
        else:
            if tab_3_med_history_combo.get() == '(No data yet)':
                tab_3_med_history_combo.set('')

            tab_3_med_history_combo.configure(values=list(
                medical_image_history.keys()),
                state='readonly')

            tab_3_med_display_button.configure(state='normal')
            # tab_3_ecg_download_button will be activated by the click on
            # the OK button on tab 3

    def tab_1_ok_cmd():
        """Command function for when the OK button on tab 1 is clicked

        When the OK button on tab 1 is clicked, this function will be
        triggered to reset tab 2 and 3, and call on
        tab_1_ok_button_click_and_auto_update_core() to update tab 1, 2, and 3

        Returns:
            None
        """
        # 1. Get data from gui
        # 2. Call other functions
        # 3. Update gui

        # This is when the user clicks on the OK button on tab 1
        record_number_content = combobox_clean_widget_only(
            tab_1_record_number_combo)

        # Only reset tab 2 and 3 when the user clicks on the OK button on tab
        # 1. These should be outside of
        # tab_1_ok_button_click_and_auto_update_core() to avoid the
        # auto_update() from keeping reseting tab 2 and tab 3
        tab_2_back_to_default()
        tab_3_back_to_default()

        tab_1_ok_button_click_and_auto_update_core(record_number_content)
        # This will update widgets on tab 1, 2, and 3

    def tab_1_cancel_cmd():
        """Give the uesr an option to leave the GUI

        This function will be triggered when the Cancel button on tab 1 is
        clicked. It will open a message window to ask whether the user
        want to leave the GUI

        Returns:
            None
        """
        # Simple button to ask whether uesr want to quit the GUI
        user_selection = messagebox.askokcancel(
            title='Warning', message='Do '
                                     'you want to '
                                     'leave the '
                                     'Monitroing GUI?')
        if user_selection is True:
            root.destroy()

    def tab_2_ok_cmd():
        """Command function for when the OK button on tab 2 is clicked

        When the OK button on tab 2 is clicked, this function will clean up
        the ECG history combobox, display the selected ECG image and
        timestamp, and activate the download button on tab 2

        Returns:
            None
        """
        ecg_selected_timestamp = combobox_clean_widget_only(
            tab_2_ecg_history_combo)
        if ecg_selected_timestamp == '':  # User made no selection
            messagebox.showwarning('Warning', 'Select an ECG image in the '
                                              'dropdown menu first to '
                                              'display')
            for widget in [tab_2_ecg_download_combo,
                           tab_2_ecg_download_button]:
                widget.configure(state='disabled')  # If there's at least 1
                # ECG history, the user must display that image first before
                # making a download
        else:
            tab_2_ecg_selected_timestamp_label.configure(
                text=ecg_selected_timestamp)

            tab_2_ecg_download_combo['state'] = 'readonly'
            tab_2_ecg_download_combo.current(0)  # The default will be the left
            # image (latest ECG image) to download
            tab_2_ecg_download_button['state'] = 'normal'

            selected_record_number = tab_1_selected_record_number_label['text']

            patient_info_dict = get_patient_data(selected_record_number)
            organized_patient_info_dict = organize_patient_info_for_GUI(
                patient_info_dict)

            selected_ecg_img_b64_str = organized_patient_info_dict[
                'ecg_image_history'][ecg_selected_timestamp]
            selected_ecg_img_ndarray = convert_b64_str_to_ndarray(
                selected_ecg_img_b64_str)
            selected_ecg_img_tk_img = convert_ndarray_to_tk_image(
                selected_ecg_img_ndarray)

            for widget in [tab_2_ecg_selected_img_label,
                           tab_2_ecg_selected_timestamp_label]:
                widget.configure(background='white')

            tab_2_ecg_selected_img_label.configure(
                image=selected_ecg_img_tk_img)
            tab_2_ecg_selected_img_label.image = selected_ecg_img_tk_img

    def tab_2_download_cmd():
        """Command function for when the Download button on tab 2 is clicked

        When the Download button on tab 2 is clicked, this function will
        start the image download process for the selected ECG

        Returns:
            None
        """
        user_selection_for_download = tab_2_ecg_download_combo.get()
        if user_selection_for_download == '':
            messagebox.showwarning('Warning', 'Select an ECG image to '
                                              'download.')
        else:
            file_direct = filedialog.asksaveasfilename(
                filetypes=[('JPG Image', '.jpg')],
                defaultextension='.jpg',
                initialdir='.\\downloaded_images\\'
            )

            record_number_content = tab_1_selected_record_number_label['text']

            patient_info_dict = get_patient_data(record_number_content)
            organized_patient_info_dict = organize_patient_info_for_GUI(
                patient_info_dict)

            if user_selection_for_download == 'Latest ECG image (Left)':
                user_selected_timestamp = tab_2_ecg_latest_timestamp_label[
                    'text']
            elif user_selection_for_download == 'Historical ECG image (Right)':
                user_selected_timestamp = \
                    tab_2_ecg_selected_timestamp_label['text']
            else:
                messagebox.showwarning('Warning', 'Something is wrong.')
                # There shouldn't be a 3rd option

            user_selected_ecg_img_b64_str = organized_patient_info_dict[
                'ecg_image_history'][user_selected_timestamp]

            if b64_str_to_img_download(user_selected_ecg_img_b64_str,
                                       file_direct) == 0:
                messagebox.showinfo(title='Downloaded', message='Image '
                                                                'sucessfully '
                                                                'downloaded!')
            else:
                messagebox.showwarning(title='Warning', message='Image '
                                                                'download '
                                                                'process is '
                                                                'given up!')

            tab_2_ecg_download_combo.set('')  # Clean up the dropdown menu

    def tab_3_ok_cmd():
        """Command function for when the OK button on tab 3 is clicked

        When the OK button on tab 3 is clicked, this function will clean up
        the medical image history combobox, display the selected medical
        image and timestamp, and activate the download button on tab 3

        Returns:
            None
        """
        med_selected_timestamp = combobox_clean_widget_only(
            tab_3_med_history_combo)
        if med_selected_timestamp == '':
            messagebox.showwarning('Warning', 'Select a medical image in the '
                                              'dropdown menu first to '
                                              'display')

            tab_3_med_download_button.configure(state='disabled')
        else:
            tab_3_med_selected_timestamp_label.configure(
                text=med_selected_timestamp)

            tab_3_med_download_button.configure(state='normal')

            selected_record_number = tab_1_selected_record_number_label['text']

            patient_info_dict = get_patient_data(selected_record_number)
            organized_patient_info_dict = organize_patient_info_for_GUI(
                patient_info_dict)

            historical_med_img_timestamp = \
                tab_3_med_selected_timestamp_label['text']

            selected_med_img_b64_str = organized_patient_info_dict[
                'medical_image_history'][historical_med_img_timestamp]

            selected_med_img_ndarray = convert_b64_str_to_ndarray(
                selected_med_img_b64_str)
            selected_med_img_tk_img = convert_ndarray_to_tk_image(
                selected_med_img_ndarray)

            for widget in [tab_3_med_selected_img_label,
                           tab_3_med_selected_filename_label,
                           tab_3_med_selected_timestamp_label]:
                widget.configure(background='white')

            tab_3_med_selected_img_label.configure(
                image=selected_med_img_tk_img)
            tab_3_med_selected_img_label.image = selected_med_img_tk_img

            tab_3_med_selected_filename_label.configure(
                text=organized_patient_info_dict[
                    'medical_filename_history'][
                    historical_med_img_timestamp])

    def tab_3_download_cmd():
        """Command function for when the Download button on tab 3 is clicked

        When the Download button on tab 3 is clicked, this function will
        start the image download process for the selected medical image

        Returns:
            None
        """
        user_selected_med_img_timestamp_for_download = \
            tab_3_med_selected_timestamp_label['text']

        # user_selected_med_img_timestamp_for_download can never be '(
        # Empty)' since tab  3's Download button need tab 3's OK button to
        # activate, which will never lead to '(Empty)' on
        # tab_3_med_selected_timestamp_label

        # Also user_selected_med_img_timestamp_for_download can never be '(
        # No data yet)' since tab 3 will be locked up if the patient has no
        # medical image history

        file_direct = filedialog.asksaveasfilename(
            filetypes=[('JPG Image', '.jpg')],
            defaultextension='.jpg',
            initialdir='.\\downloaded_images\\'
        )

        record_number_content = tab_1_selected_record_number_label['text']

        patient_info_dict = get_patient_data(record_number_content)
        organized_patient_info_dict = organize_patient_info_for_GUI(
            patient_info_dict)

        historical_med_img_timestamp = tab_3_med_selected_timestamp_label[
            'text']

        selected_med_img_b64_str = organized_patient_info_dict[
            'medical_image_history'][historical_med_img_timestamp]

        if b64_str_to_img_download(selected_med_img_b64_str,
                                   file_direct) == 0:
            messagebox.showinfo(title='Downloaded', message='Image '
                                                            'sucessfully '
                                                            'downloaded!')
        else:
            messagebox.showwarning(title='Warning', message='Image '
                                                            'download '
                                                            'process is '
                                                            'given up!')
        tab_3_med_history_combo.set('')  # Clean up the dropdown menu

    def tab_1_lock():
        """Lock up tab 1 Basic patient information

        This function resets tab 1 Basic patient information and lock it up

        Returns:
            None
        """
        tab_1_back_to_default()
        tab_control.tab(tab_1, state='disabled')

    def tab_1_back_to_default():
        """Reset tab 1 Basic patient information

        This function returns all the labels in tab 1 Basic patient
        information back to default state as "(Empty)" in yellow background

        Returns:
            None
        """
        tab_1_record_number_combo.set('')

        for widget in [tab_1_selected_record_number_label,
                       tab_1_patient_name_label,
                       tab_1_latest_heart_rate_label,
                       tab_1_latest_heart_rate_time_label]:
            widget.configure(text='(Empty)', background='yellow')

    def tab_2_lock():
        """Lock up tab 2 ECG images

        This function resets tab 2 ECG images and lock it up

        Returns:
            None
        """
        tab_2_back_to_default()
        tab_control.tab(tab_2, state='disabled')

    def tab_2_back_to_default():
        """Reset tab 2 ECG images

        This function returns all the labels in 2 ECG images back to default
        state as "(Empty)" in yellow background, all the combobox as cleaned
        up and deactivated, all the button as deactivated

        Returns:
            None
        """

        tab_2_ecg_history_combo.set('')
        tab_2_ecg_download_combo.set('')

        for widget in [tab_2_ecg_latest_img_label,
                       tab_2_ecg_selected_img_label]:
            widget.configure(image='', background='yellow')

        for widget in [tab_2_ecg_latest_img_label,
                       tab_2_ecg_latest_timestamp_label,
                       tab_2_ecg_selected_img_label,
                       tab_2_ecg_selected_timestamp_label]:
            widget.configure(text='(Empty)', background='yellow')

        for widget in [tab_2_ecg_history_combo,
                       tab_2_ecg_display_button,
                       tab_2_ecg_download_combo,
                       tab_2_ecg_download_button]:
            widget.configure(state='disabled')
        pass

    def tab_3_lock():
        """Lock up tab 3 Medical images

        This function resets tab 3 Medical images and lock it up

        Returns:
            None
        """
        tab_3_back_to_default()
        tab_control.tab(tab_3, state='disabled')

    def tab_3_back_to_default():
        """Reset tab 3 Medical images

        This function returns all the labels in 3 Medical images back to
        default state as "(Empty)" in yellow background, all the combobox as
        cleaned up and deactivated, all the button as deactivated

        Returns:
            None
        """
        tab_3_med_history_combo.set('')

        tab_3_med_selected_img_label.configure(image='', background='yellow')

        for widget in [tab_3_med_selected_img_label,
                       tab_3_med_selected_filename_label,
                       tab_3_med_selected_timestamp_label]:
            widget.configure(text='(Empty)', background='yellow')

        for widget in [tab_3_med_display_button, tab_3_med_download_button]:
            widget.configure(state='disabled')
        pass

    def auto_update():
        """Auto update to obtain the latest data from database

        This function automatically update the GUI with the latets data
        obtained from the database every 1 sec. It only checks the status of
        the database of no record number has been selected. If a record
        number has been selected, it will update the patient name, latets
        heart rate and its timestamp, latest ECG and its timestamp,
        all possible options for ECG history and medical image history
        comboboxes on tab 2 and 3 respectively

        Returns:
            None
        """
        all_med_number_list = get_all_med_number()

        database_status = update_database_status(all_med_number_list)  # Update
        # the root window
        # title, tab 0's dtabase status label, and tab 1, 2, and 3's states
        # based on the status base status

        record_number_content = tab_1_selected_record_number_label['text']
        tab_1_record_number_combo.configure(values=get_all_med_number())
        if record_number_content == '(Empty)':
            pass
        elif record_number_content not in all_med_number_list:
            messagebox.showwarning('Warning',
                                   'Previous patient number does '
                                   'not exist anymore. Please make a'
                                   ' new selection.')
            tab_1_back_to_default()
        else:  # Selected medical record number as shown on tab 1 is still in
            # the database
            tab_1_ok_button_click_and_auto_update_core(
                record_number_content)  # Mainly update tab 1

            # Obtain the latest patient information
            patient_info_dict = get_patient_data(record_number_content)
            organized_patient_info_dict = organize_patient_info_for_GUI(
                patient_info_dict)

            tab_1_ok_button_click_and_auto_update_core(
                record_number_content)  # Mainly update for tab 2 and 3

        root.after(1000, auto_update)

    def update_database_status(all_med_number_list):
        """Update the database status on tab 0

        This function automatically check for whether the database is empty.
        Based on the result, it updates the message on tab 0 and the
        lock/unlock status of tab 1, 2, and 3

        Returns:
            database_status (bool): True if the database is not empty and
            False if the database is empty
        """
        # Obtain root window title for later update
        root_title_str = root.title()
        if '(' in root_title_str:
            root_title_str = root_title_str.split('(')[0].strip()  # Avoid the
            # title from accumulating the status string

        if all_med_number_list == [
            '(Server database is empty. Have at least 1 patient entry to '
                'proceed.)']:  # If database is empty
            title_database_status_str = ' (Deactivated. Database is empty!)'

            # Reset and deactivate all the tab_1, tab_2, tab_3 if the database
            # is empty
            tab_1_lock()
            tab_2_lock()
            tab_3_lock()

            database_status_label_str = 'Database is empty! We are checking ' \
                                        'the database constantly for ' \
                                        'updates...'
            database_status_label_background_color = 'red'
            database_status = False

        else:  # If database contains at least 1 patient's info
            title_database_status_str = ' (Active. Database is not empty.)'

            tab_control.tab(tab_1, state='normal')  # Activate the
            # tab_1 tab so the user can continue

            database_status_label_str = 'Database is not empty. You can ' \
                                        'proceed to the next tab now. ' \
                                        'Database status will be ' \
                                        'dynamically ' \
                                        'updated.'
            database_status_label_background_color = 'green'
            database_status = True

        root.title(root_title_str + title_database_status_str)  # Update root
        # window title based on database status
        tab_0_database_status_label.configure(
            text=database_status_label_str,
            background=database_status_label_background_color
        )

        return database_status

    r = requests.get(url + "/api/monitor/database_connect_status")
    if r.status_code == 200:  # Then the database is successfully connected to
        # the server

        # Initial set up for all the elements
        root, tab_control, tab_0, tab_1, tab_2, tab_3 = main_root_tab_setup()

        # Set up tab_0
        tab_0_database_status_label = tab_0_setup()

        # Set up tab_1
        tab_1_ok_button, tab_1_cancel_button, tab_1_record_number_combo, \
            tab_1_selected_record_number_label, tab_1_patient_name_label, \
            tab_1_latest_heart_rate_label, \
            tab_1_latest_heart_rate_time_label = tab_1_setup()

        # Set up tab_2
        tab_2_ecg_latest_img_label, tab_2_ecg_latest_timestamp_label, \
            tab_2_ecg_history_combo, tab_2_ecg_display_button, \
            tab_2_ecg_selected_img_label, tab_2_ecg_selected_timestamp_label, \
            tab_2_ecg_download_combo, tab_2_ecg_download_button = tab_2_setup()

        # Set up tab_3
        tab_3_med_history_combo, tab_3_med_display_button, \
            tab_3_med_selected_img_label, tab_3_med_selected_filename_label, \
            tab_3_med_selected_timestamp_label, \
            tab_3_med_download_button = tab_3_setup()

        auto_update()
        root.mainloop()
    else:  # Notify the user if there is any issue for the server to connect
        # to the database
        messagebox.showwarning('Warning',
                               'Server has issues on connecting to the '
                               'server.')
    return 0


if __name__ == '__main__':
    main_window()
