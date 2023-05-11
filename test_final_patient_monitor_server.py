import pytest
from pymodm import connect
from database_definition import Patient


# **************************Junqi Lu starts**************************
@pytest.mark.parametrize('connect_str, expect_result',
                         [(
                                 'mongodb+srv://davidhe:Davidhe1998@cluster0'
                                 '.grsdcun.mongodb.net'
                                 '/dummy_dataset'
                                 '?retryWrites=true&w=majority', False), (
                                 'mongodb+srv://davidhe:Davidhe1998@cluster0'
                                 '.grsdcun.mongodb.net'
                                 '/empty_dataset'
                                 '?retryWrites=true&w=majority', True)

                          ]
                         )
def test_empty_db_judge(connect_str, expect_result):
    from final_patient_monitor_server import empty_db_judge
    try:
        connect(connect_str)
    except (Exception,):
        assert False
    result = empty_db_judge()
    assert result == expect_result


@pytest.mark.parametrize('connect_str, expect_msg, expect_status',
                         [("non_existing_database_str",
                           'Failed to connect to the '
                           'database', 400),
                          (
                          "mongodb+srv://davidhe:Davidhe1998@cluster0"
                          ".grsdcun.mongodb.net"
                          "/Final_project?retryWrites=true&w=majority",
                          'Successfully '
                          'connected to the '
                          'database', 200)

                          ]
                         )
def test_init_database(connect_str, expect_msg, expect_status):
    from final_patient_monitor_server import init_database

    msg, status = init_database(connect_str)
    assert msg == expect_msg
    assert status == expect_status


@pytest.mark.parametrize('connect_str, empty_db_judgement, '
                         'expected_return_list, '
                         'expected_status', [
                             ('mongodb+srv://davidhe:Davidhe1998@cluster0'
                              '.grsdcun.mongodb.net'
                              '/empty_dataset'
                              '?retryWrites=true&w=majority', True,
                              ['Database is'
                               ' empty. Add in data from patient GUI first'],
                              400),
                             ('mongodb+srv://davidhe:Davidhe1998@cluster0'
                              '.grsdcun.mongodb.net'
                              '/dummy_dataset'
                              '?retryWrites=true&w=majority', False,
                              [0, 1, 2, 3, 4, 5, 6, 7, 8], 200)
                         ])
def test_get_all_med_number_worker(connect_str, empty_db_judgement,
                                   expected_return_list,
                                   expected_status):
    from final_patient_monitor_server import get_all_med_number_worker
    try:
        connect(connect_str)
    except (Exception,):
        assert False
    return_list, status = get_all_med_number_worker(empty_db_judgement)
    assert return_list == expected_return_list
    assert status == expected_status


@pytest.mark.parametrize('record_number, expected_dict, expected_status', [
    (7, {'ecg_image_history': {}, 'heart_rate_history': {},
         'medical_filename_history': {}, 'medical_image_history': {},
         'medical_record_number': 7, 'patient_name': None}, 200),
    (100, {}, 200),
    (3, {'ecg_image_history': {}, 'heart_rate_history': {},
         'medical_filename_history': {}, 'medical_image_history': {},
         'medical_record_number': 3, 'patient_name': 'G H'}, 200),
    (8, {'ecg_image_history': {}, 'heart_rate_history': {},
         'medical_filename_history': {'2022-12-05 22:15:17': 'med_img.jpg'},
         'medical_image_history': {
             '2022-12-05 22:15:17': '/9j/4AAQSkZJRgABAQEAwADAA'
                                    'AD/2wBDAAgGBgcGBQgHBwcJCQgKDBQN'
                                    'DAsLDBkSEw8UHRofHh0aHBwgJC4n'
                                    'ICIsIxwcKDcpLDAxNDQ0Hyc5PTg'
                                    'yPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRw'
                                    'hMjIyMjIyMjIyMjIyMjIyMjIyM'
                                    'jIyMjIyMjIyMjIyMjIyMjIyMjI'
                                    'yMjIyMjIyMjIyMjL/wAARCAAJA'
                                    'AkDAREAAhEBAxEB/8QAFQABAQA'
                                    'AAAAAAAAAAAAAAAAABwT/xAAfEA'
                                    'ABAwMFAAAAAAAAAAAAAAABAAQRAgUH'
                                    'EjRSccH/xAAUAQEAAAAAAAAAAAAAAAAA'
                                    'AAAA/8QAFBEBAAAAAAAAAAAAAAAAAA'
                                    'AAAP/aAAwDAQACEQMRAD8Akx03Di4EkTo'
                                    'goFmaeKA0xnvHHXiBKQf/2Q=='},
         'medical_record_number': 8, 'patient_name': None}, 200)
])
def test_retrieve_patient_info_worker(record_number, expected_dict,
                                      expected_status):
    from final_patient_monitor_server import retrieve_patient_info_worker
    try:
        connect('mongodb+srv://davidhe:Davidhe1998@cluster0'
                '.grsdcun.mongodb.net'
                '/dummy_dataset'
                '?retryWrites=true&w=majority')
    except (Exception,):
        assert False
    result_dict, status = retrieve_patient_info_worker(record_number)
    assert result_dict == expected_dict
    assert status == expected_status

# **************************Junqi Lu ends**************************

# **************************Ramana Balla starts**************************
# **************************Ramana Balla ends**************************

# **************************Ziwei He starts**************************


@pytest.mark.parametrize("in_data, warn, delete, exp_msg, exp_code, entry", [
    ({"patient_record_no": 1, "patient_name": '', "medical_img": '',
      "img_filename": '', "ECG_img": '', "heart_rate": ''}, "false",
     False, "Successfully upload the patient information", 201,
     Patient(medical_record_number=1)),
    ({"patient_record_no": 1, "patient_name": 'David', "medical_img": '',
      "img_filename": '', "ECG_img": '', "heart_rate": ''}, "false",
     False, "Successfully update the information of patient 1", 201,
     Patient(medical_record_number=1, patient_name="David")),
    ({"patient_record_no": 1, "patient_name": '', "medical_img": '',
      "img_filename": '', "ECG_img": 'gg', "heart_rate": '80'}, "false",
     False, "Successfully update the information of patient 1", 201,
     Patient(medical_record_number=1, patient_name="David")),
    ({"patient_record_no": 1, "patient_name": '', "medical_img": '',
      "img_filename": '', "ECG_img": '', "heart_rate": ''}, "false",
     False, "No information need to be updated", 201,
     Patient(medical_record_number=1, patient_name="David")),
    ({"patient_record_no": 1, "patient_name": 'David', "medical_img": '',
      "img_filename": '', "ECG_img": '', "heart_rate": ''}, "false",
     False, "No information need to be updated", 201,
     Patient(medical_record_number=1, patient_name="David")),
    ({"patient_record_no": 1, "patient_name": 'David', "medical_img": 'UU',
      "img_filename": '1.jpg', "ECG_img": '', "heart_rate": ''}, "false",
     False, "Successfully update the information of patient 1", 201,
     Patient(medical_record_number=1, patient_name="David")),
    ({"patient_record_no": 1, "patient_name": 'Davi', "medical_img": 'VV',
      "img_filename": '2.jpg', "ECG_img": 'hh', "heart_rate": '70'}, "false",
     False, "Need confirmation for overwriting old name", 200,
     Patient(medical_record_number=1, patient_name="David")),
    ({"patient_record_no": 1, "patient_name": 'Davi', "medical_img": '',
      "img_filename": '', "ECG_img": '', "heart_rate": ''}, "true",
     False, "Name updated", 201,
     Patient(medical_record_number=1, patient_name="Davi")),
    ({"patient_record_no": 1, "patient_name": 'Davi', "medical_img": 'VV',
      "img_filename": '2.jpg', "ECG_img": 'hh', "heart_rate": '70'}, "true",
     True, "Successfully update the information of patient 1", 201,
     Patient(medical_record_number=1, patient_name="Davi"))
])
def test_info_process(in_data, warn, delete, exp_msg, exp_code, entry):
    from final_patient_monitor_server import info_process
    connect("mongodb+srv://davidhe:Davidhe1998@cluster0.grsdcun.mongodb.net/"
            "test?retryWrites=true&w=majority")
    msg, status = info_process(in_data, warn)
    x = Patient.objects.raw({"_id": 1}).first()
    if x.ecg_image_history != {}:
        time = list(x.ecg_image_history.keys())
        if len(time) == 1:
            entry.ecg_image_history = {time[0]: 'gg'}
            entry.heart_rate_history = {time[0]: 80}
        else:
            entry.ecg_image_history = {time[0]: 'gg', time[1]: 'hh'}
            entry.heart_rate_history = {time[0]: 80, time[1]: 70}
    if x.medical_image_history != {}:
        time = list(x.medical_image_history.keys())
        if len(time) == 1:
            entry.medical_image_history = {time[0]: 'UU'}
            entry.medical_filename_history = {time[0]: "1.jpg"}
        else:
            entry.medical_image_history = {time[0]: 'UU', time[1]: 'VV'}
            entry.medical_filename_history = {time[0]: "1.jpg",
                                              time[1]: '2.jpg'}
    if delete:
        x.delete()
    assert msg == exp_msg
    assert status == exp_code
    assert x == entry


@pytest.mark.parametrize("in_data, first, delete, entry", [
    ({"patient_record_no": 1, "patient_name": 'David', "medical_img": 'VV',
      "img_filename": '1.jpg', "ECG_img": 'hh', "heart_rate": '60'}, True,
     False, Patient(medical_record_number=1, patient_name="David")),
    ({"patient_record_no": 1, "patient_name": '', "medical_img": 'WW',
      "img_filename": '2.jpg', "ECG_img": '', "heart_rate": ''}, False, False,
     Patient(medical_record_number=1, patient_name="David")),
    ({"patient_record_no": 1, "patient_name": 'Davi', "medical_img": '',
      "img_filename": '', "ECG_img": 'ii', "heart_rate": '70'}, False, True,
     Patient(medical_record_number=1, patient_name="Davi"))
])
def test_save_info(in_data, first, delete, entry):
    from final_patient_monitor_server import save_info
    connect("mongodb+srv://davidhe:Davidhe1998@cluster0.grsdcun.mongodb.net/"
            "test?retryWrites=true&w=majority")
    save_info(in_data, first)
    x = Patient.objects.raw({"_id": 1}).first()
    time_ecg = list(x.ecg_image_history.keys())
    if len(time_ecg) == 1:
        entry.ecg_image_history = {time_ecg[0]: 'hh'}
        entry.heart_rate_history = {time_ecg[0]: 60}
    else:
        entry.ecg_image_history = {time_ecg[0]: 'hh', time_ecg[1]: 'ii'}
        entry.heart_rate_history = {time_ecg[0]: 60, time_ecg[1]: 70}

    time_img = list(x.medical_image_history.keys())
    if len(time_img) == 1:
        entry.medical_image_history = {time_img[0]: 'VV'}
        entry.medical_filename_history = {time_img[0]: "1.jpg"}
    else:
        entry.medical_image_history = {time_img[0]: 'VV', time_img[1]: 'WW'}
        entry.medical_filename_history = {time_img[0]: "1.jpg",
                                          time_img[1]: '2.jpg'}
    if delete:
        x.delete()
    assert x == entry
# **************************Ziwei He ends**************************
