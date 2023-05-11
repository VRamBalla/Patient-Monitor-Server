import pymongo.errors
from database_definition import Patient
from pymodm import connect
from flask import Flask, request, jsonify
from pymodm import errors as pymodm_errors
from datetime import datetime


app = Flask(__name__)


@app.route('/', methods=['GET'])
def server_on():
    """Indicate server status

    This route is a simple route to indicate that the server is on

    Returns:
        'Server is on' (str): a simple string to indicate that the server is on
    """
    return 'Server is on'


# **************************Junqi Lu starts**************************


@app.route('/api/monitor/database_connect_status', methods=['GET'])
def get_database_connect_status_handler():
    """Handler function that checks on the connection of the database

    This handler function calls on init_database() to try to connect to a
    database and return responses to the client to indicate the status of
    the connection

    Returns:
        jsonify(msg) (jsonified str): jsonified 'Successfully connected
    to the database' if the database is successfully connected and 'Failed
    to connect to the database' if not

        status (int): this is the value to indicate the database connection
        status. 200 if the database is successfully connected and 400 if not
    """
    database_connection_str = \
        "mongodb+srv://davidhe:Davidhe1998@cluster0.grsdcun.mongodb.net" \
        "/Final_project?retryWrites=true&w=majority"  # This is the formal
    # final project database
    # database_connection_str = \
    #     "mongodb+srv://davidhe:Davidhe1998@cluster0.grsdcun.mongodb.net" \
    #     "/dummy_dataset?retryWrites=true&w=majority"  # This is the
    # # dummy_dataset for development. This will be commented out in the final
    # # code

    msg, status = init_database(database_connection_str)

    return jsonify(msg), status


def init_database(database_connection_str):
    """Initialize the databases by trying to connect to a MongoDB database

    This function is the real worker function that simply connects to a
    database in
    MongoDB using a try-except
    block by the database_connection_str. It will return corresponding
    messages and status code to indicate the connection status to the database

    Args:
        database_connection_str (str): the connection str obtained from
        mongodb to connect to a specific database

    Returns:
        msg (str): 'Successfully connected to the database' if the
    database is successfully connected and 'Failed to connect to the
    database' if not

        status (int): this is the value to indicate the database connection
        status. 200 if the database is successfully connected and 400 if not
    """
    try:
        connect(database_connection_str)
    except (Exception,):
        status = 400
        msg = 'Failed to connect to the database'
    else:
        status = 200
        msg = 'Successfully connected to the database'

    return msg, status


@app.route('/api/monitor/all_med_number', methods=['GET'])
def get_all_med_number_handler():
    """Obtain all the medical record numbers in the connected database

    This function is the handler of the route '/api/monitor/all_med_number'.
    It first calls on a function that judges whether the connected database
    is empty, and then calls on get_all_med_number_worker() that will obtain
    all the record number if there's at least 1 or ['Database is empty. Add
    in data from patient GUI first'] if there's none. Finally, it returns
    the obtained record number list back to the client with the status code.

    Returns:
        jsonify(all_med_number_list): all_med_number_list will be a list
        that contains all the medical record number in the database or
        simply ['Database is empty. Add in data from patient GUI first'] if
        the database has no record at all. It will be jsonified to send
        back to the client
        status (int): 200 if the database has at least 1 record; 400 if the
        database has no records at all
    """
    # You do not have to test the Flask handler functions directly

    # Since there's no input data, this route's handler start from complete
    # tasks
    empty_db_judgement = empty_db_judge()
    all_med_number_list, status = get_all_med_number_worker(
        empty_db_judgement)

    # Return the JSON str and status code back to requestor
    return jsonify(all_med_number_list), status


def get_all_med_number_worker(empty_db_judgement):
    """The real working function that obtain all the medical record number
    in the database

    Based on the empty_db_judgement, this function decides whether to simply
    return ['Database is empty. Add in data from patient GUI first'],
    400 to indicate the database is empty or to iterate through all the
    record numbers in the database to make a list and return that list with
    200

    Returns:
        med_number_list (list of int): if the database contains at
    least 1 record number, it contains all the record number in the type of
    int; if the database is empty, then this will be ['Database is empty.
    Add in data from patient GUI ' 'first']

        status (int): 200 if the database has at least 1 record; 400 if the
        database has no records at all

    """
    med_number_list = []
    if empty_db_judgement is True:
        med_number_list = ['Database is empty. Add in data from patient GUI '
                           'first']
        status = 400
    else:

        for patient in Patient.objects.raw({}):
            med_number = patient.medical_record_number
            med_number_list.append(med_number)
        status = 200
    return med_number_list, status


def empty_db_judge():
    """Judges whether a conencted database is empty

    This function iterates through all the entries in the connected database
    to count out the number of entries. If the number of entry is 0,
    it returns True to indicate the connected database is empty and false if
    it is not empty

    Returns:
        True or False (bool): the judgement of whether the connected
        database is empty. True if empty and False if not empty
    """
    count = 0
    try:
        for patient in Patient.objects.raw({}):
            print(patient)
            count += 1
    except (Exception,):
        return True  # Consider a non-working database pretty much the same
        # as an empty database
    else:
        if count == 0:
            return True
        else:
            return False


@app.route('/api/monitor/patient_info/<record_number>', methods=['GET'])
def retrieve_patient_info_handler(record_number):
    """Recieve record number from route request and return the patient info
    based on that record number

    This function is the handler of the route
    '/api/monitor/patient_info/<record_number>'. It first receives input
    record number from the request. Then with supporting functions,
    it returns the found patient info dict from the database. Note that this
    route will only used by an GUI that asks user to select a record number
    from available record number inside the database. Since the patient info
    input GUI has already checked the data type of record number as int,
    this route doesn't check again on whether that record number exist in
    the database and whether it is an int--both are guuarnteed by the
    patient info input GUI.

    Args:
        record_number (int): a unique int that distinguishes a patient's
        entry from others'

    Returns:
        jsonify(all_med_number_list): all_med_number_list will be a list
        that contains all the medical record number in the database or
        simply ['Database is empty. Add in data from patient GUI first'] if
        the database has no record at all. It will be jsonified to send
        back to the client
        status (int): 200 if the database has at least 1 record; 400 if the
        database has no records at all
    """
    # You do not have to test the Flask handler functions directly

    # No value judgement is needed since record_number is selected by the user
    # from the database (users not allowed to type anything), and we have
    # data validation at the patient
    # GUI to
    # ensure record_number follows the correct data type.

    patient_info_dict, status = retrieve_patient_info_worker(record_number)

    # Return the JSON str and status code back to requestor
    return jsonify(patient_info_dict), status


def retrieve_patient_info_worker(record_number):
    """The real working function that obtain the patient info by the given
    record number

    Based on the given record_number, this function uses a try-except block
    to go through all the records and try to obtain the patinet info based
    on the given record number.

    Args:
        record_number (int): a unique int that distinguishes a patient's
        entry from others'

    Returns:
        output (str or dict): can be 'Something is wrong' if the searching
        run into some issues or patient_info_dict if the corresponding
        patient info dict was found by the given record number. If a dict,
        the format for output will be {
    medical_record_number: int, patient_name: str, heart_rate_history: {
    timestmap_str: int}, ecg_image_history: {timestmap_str: b64_str},
    medical_filename_history: {timestmap_str: filename_str},
    medical_image_history: {timestmap_str: b64_str}}

        status (int): 200 if the corresponding info dict was successfully
        obtained; 400 if the searching was not successful
    """
    record_number = int(record_number)
    patient_info_dict = {}
    try:
        for patient in Patient.objects.raw({'_id': record_number}):
            patient_info_dict[
                'medical_record_number'] = patient.medical_record_number
            patient_info_dict[
                'patient_name'] = patient.patient_name
            patient_info_dict[
                'heart_rate_history'] = patient.heart_rate_history
            patient_info_dict[
                'ecg_image_history'] = patient.ecg_image_history
            patient_info_dict[
                'medical_filename_history'] = patient.medical_filename_history
            patient_info_dict[
                'medical_image_history'] = patient.medical_image_history
    except (Exception,):
        output = 'Something is wrong'
        status = 400
    else:  # Since patient wil only make a selection from a list of all the
        # record number in the database, if the request was made with a
        # non-existing record number, this will return patient_info_dict as
        # {} but still a status code 200. But this case will never happen if
        # the user makes requests through GUI only
        output = patient_info_dict
        status = 200

    return output, status


# **************************Junqi Lu ends**************************

# **************************Ramana Balla starts**************************
# **************************Ramana Balla ends**************************

# **************************Ziwei He starts**************************


@app.route("/patient_GUI/upload/<warn>", methods=["POST"])
def upload_handler(warn):
    """Upload patient information handler

    Accept patient information upload. The patient information should be
    formatted as below:
        {
            "patient_record_no": <int> (mandatory)
            "patient_name": <str> (blank if not provide)
            "medical_img": <b64str> (blank if not provide)
            "img_filename": <str> (blank if not provide)
            "ECG_img": <b64str> (blank if not provide)
            "heart_rate": <str> (blank if not provide)
        }
    The <warn> parameter indicates if the user wants to overwrite data. "true"
    means overwrite. Otherwise, the parameter is "false"

    Args:
        warn (string): "true" if the user confirms overwriting. Otherwise, it
        is "false"

    Returns:
        msg (string): Status message.
        status (integer): status code.

    """
    in_data = request.get_json()
    msg, status = info_process(in_data, warn)
    return msg, status


def info_process(in_data, warn):
    """Process the patient information and return the result of processing.

    This function checks for the existing information of a record number in the
    database. If no record found, the information will be stored in the
    database. If there is existing record, this function updates the record
    unless the name in the record is different from the one provided by the
    user. Confirmation of the user is required to update the name in the
    database.

    Args:
        in_data (dictionary): Patient information in the format of:
            {
                "patient_record_no": <int> (mandatory),
                "patient_name": <str> (blank if not provide),
                "medical_img": <b64str> (blank if not provide),
                "img_filename": <str> (blank if not provide),
                "ECG_img": <b64str> (blank if not provide),
                "heart_rate": <str> (blank if not provide),
            }
        warn (string): "true" if the user confirms overwriting. Otherwise, it
        is "false"

    Returns:
        msg (string): Status message.
        status (integer): status code.

    """
    if warn == "false":
        try:
            x = Patient.objects.raw({"_id": in_data["patient_record_no"]}). \
                first()
            if x.patient_name != in_data["patient_name"]:
                if x.patient_name is not None and \
                        in_data["patient_name"] != '':
                    msg = "Need confirmation for overwriting old name"
                    status = 200
                    return msg, status
                else:
                    save_info(in_data, False)
                    status = 201
                    if [in_data["patient_name"], in_data["ECG_img"],
                            in_data["medical_img"]] == ['', '', '']:
                        msg = "No information need to be updated"
                    else:
                        msg = "Successfully update the information of " + \
                              "patient {}".format(in_data["patient_record_no"])
                    return msg, status
            else:
                save_info(in_data, False)
                if [in_data["ECG_img"], in_data["medical_img"]] == \
                        ['', '']:
                    msg = "No information need to be updated"
                else:
                    msg = "Successfully update the information of patient {}".\
                        format(in_data["patient_record_no"])
                status = 201
                return msg, status
        except pymodm_errors.DoesNotExist:
            save_info(in_data, True)
            msg = "Successfully upload the patient information"
            status = 201
            return msg, status
        except (pymongo.errors.ServerSelectionTimeoutError,
                pymongo.errors.ConnectionFailure):
            msg = "Fail to connect to the database"
            status = 400
            return msg, status
    else:
        save_info(in_data, False)
        if in_data["medical_img"] == '' and in_data["ECG_img"] == '':
            msg = "Name updated"
        else:
            msg = "Successfully update the information of patient {}". \
                format(in_data["patient_record_no"])
        status = 201
        return msg, status


def save_info(in_data, first_record):
    """Save information in the database.

    This function creates new entry in the database and updates existing entry
    based on the uploaded information

    Args:
        in_data (dictionary): Patient information in the format of:
            {
                "patient_record_no": <int> (mandatory),
                "patient_name": <str> (blank if not provide),
                "medical_img": <b64str> (blank if not provide),
                "img_filename": <str> (blank if not provide),
                "ECG_img": <b64str> (blank if not provide),
                "heart_rate": <str> (blank if not provide),
            }
        first_record (boolean): True if there is no existing record in the
        database for the uploaded information. False if there is existing
        record for the uploaded information.

    Returns:
        None.

    """
    query = Patient.objects.raw({"_id": in_data["patient_record_no"]})
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if first_record:
        info = Patient(medical_record_number=in_data["patient_record_no"])
        if in_data["patient_name"] != '':
            info.patient_name = in_data["patient_name"]
        if in_data["medical_img"] != '':
            medical_img = {timestamp: in_data["medical_img"]}
            img_name = {timestamp: in_data["img_filename"]}
            info.medical_filename_history = img_name
            info.medical_image_history = medical_img
        if in_data["ECG_img"] != '':
            ECG = {timestamp: in_data["ECG_img"]}
            hr = {timestamp: int(in_data["heart_rate"])}
            info.ecg_image_history = ECG
            info.heart_rate_history = hr
        info.save()

    else:
        if in_data["patient_name"] != '':
            query.update({"$set": {"patient_name": in_data["patient_name"]}})
        if in_data["medical_img"] != '':
            query.update({"$set": {"medical_image_history.{}".
                         format(timestamp): in_data["medical_img"]}})
            query.update({"$set": {"medical_filename_history.{}".
                         format(timestamp):
                                       in_data["img_filename"]}})
        if in_data["ECG_img"] != '':
            query.update({"$set": {"ecg_image_history.{}".format(timestamp):
                                   in_data["ECG_img"]}})
            query.update({"$set": {"heart_rate_history.{}".format(timestamp):
                                   int(in_data["heart_rate"])}})
# **************************Ziwei He ends**************************


if __name__ == '__main__':
    database_connection_str = \
        "mongodb+srv://davidhe:Davidhe1998@cluster0.grsdcun.mongodb.net" \
        "/Final_project?retryWrites=true&w=majority"  # This is the formal
    # final project database

    connect(database_connection_str)
    app.run(host="0.0.0.0")  # Remote server
    # app.run()  # Local server
