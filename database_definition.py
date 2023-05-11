from pymodm import MongoModel, fields


class Patient(MongoModel):
    """Definition of a patient record in the database

    All entries should at least have the unique medical_record_number,
    which is an int. Then an entry may or may not have the following
    * patient_name in the format of a string as "Firstname Lastname"
    * Heart rate: heart_rate_history and ecg_image_history will be
    synchronized and new values will use the same timestamp_str
        * heart_rate_history (dict) in the format
        of {timestamp_str: heart_rate_int}
        * ecg_image_history (dict) in the format of {timestamp_str:
        b64_str_ecg}
    * Medical image: medical_filename_history and medical_image_history will be
    synchronized and new values will use the same timestamp_str
        * medical_filename_history (dict) in the format
        of {timestamp_str: medical_filename_str}
        * medical_image_history (dict) in the format
        of {timestamp_str: b64_str_medical}

    """
    medical_record_number = fields.IntegerField(primary_key=True)  # This
    # field should be a unique number identifier for each patient
    patient_name = fields.CharField()  # This field should be a string in the
    # format of "Firstname Lastname"

    heart_rate_history = fields.DictField()  # This field should be a dict in
    # the format of {timestamp_str: heart_rate_int}
    ecg_image_history = fields.DictField()  # This field should be a dict in
    # the format of {timestamp_str: b64_str_ecg}

    medical_filename_history = fields.DictField()  # This field should be a
    # dict in the format of {timestamp_str: medical_filename_str}
    medical_image_history = fields.DictField()  # This field should be a dict
    # in the format of {timestamp_str: b64_str_medical}
