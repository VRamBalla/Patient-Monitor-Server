#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 20:54:22 2022

@author: david
"""
from PIL import Image
import pytest


def test_img_resize():
    from patient_side_GUI import img_resize
    img = Image.open("images/acl1.jpg")
    img_resized = img_resize(img)
    x, y = img_resized.size
    assert x == 150
    assert y == 150


@pytest.mark.parametrize("filename, expect_check, expect_path, expect_file", [
    ("test data/test_data2", False, None, None),
    ("test data/blank_line.csv", False, None, None),
    ("test data/Non-increasing1.csv", False, None, None),
    ("test data/Non-increasing2.csv", False, None, None),
    ("test data/Unequal_line.csv", False, None, None),
    ("test data/short_duration.csv", False, None, None),
    ("test data/low_f.csv", False, None, None),
    ("LICENSE", False, None, None),
    ("README.md", False, None, None),
    ("test data/test.csv", True, "test data", "test.csv"),
    ("test_data3.csv", True, "", "test_data3.csv"),
    ])
def test_check_ecg_file(filename, expect_check, expect_path, expect_file):
    from patient_side_GUI import check_ecg_file
    check, path, file = check_ecg_file(filename)
    assert check == expect_check
    assert path == expect_path
    assert file == expect_file


@pytest.mark.parametrize("filename, path, expectx, expect_lgnd, expect_fname,"
                         "test_img",
                         [("test.csv", "test data", None, ["Signal"],
                           "ecg_analysis/test.jpg",
                           "ecg_analysis/test_data_testimg.jpg"),
                          ("test_data3.csv", "", [115, 409, 697, 988, 1304,
                           1613, 1910, 2201, 2488, 2781, 3072, 3372, 3691,
                           3997, 4288, 4578, 4865, 5164, 5465, 5767, 6083,
                           6380, 6664, 6951, 7241, 7548, 7856, 8159, 8472,
                           8763, 9042, 9332, 9630, 9939],
                           ["Signal", "Accepted peaks"],
                           "ecg_analysis/test_data3.jpg",
                           "ecg_analysis/test_data3_testimg.jpg")])
def test_visualization(filename, path, expectx, expect_lgnd, expect_fname,
                       test_img):
    from ecg_analysis import read_data, convert_data, split_data_and_duration
    from ecg_analysis import remove_suffix
    from patient_side_GUI import visualization
    import json
    import filecmp
    dp, _ = read_data(filename, path)
    checked, _ = convert_data(dp)
    time, voltage, _ = split_data_and_duration(checked)
    fname = remove_suffix(filename)
    fname = "ecg_analysis/" + fname + ".json"
    with open(fname, 'r') as metric:
        metrics = json.load(metric)
    x, lgnd, ecg_name = visualization(time, voltage, metrics,
                                      "ecg_analysis/"+filename)
    assert x == expectx
    assert lgnd == expect_lgnd
    assert ecg_name == expect_fname
    assert filecmp.cmp(ecg_name, test_img)


@pytest.mark.parametrize("img, expect_b64",
                         [("ecg_analysis/test.jpg", "BRRRQAUUUUAf/9k="),
                          ("images/acl1.jpg", "AUUUUAFFFFAH/9k=")])
def test_img_2_b64(img, expect_b64):
    from patient_side_GUI import img_2_b64
    b64str = img_2_b64(img)
    assert b64str[-16:] == expect_b64


@pytest.mark.parametrize("record, expect_tag, expect_record", [
    ('', 'Empty record', ''), ('    ', 'Empty record', ''),
    (' 1 2s ', 'Invalid record', ''), ('/', 'Invalid record', ''),
    ('02', 'pass', '02'), (' 7 2 ', 'pass', '72')])
def test_validate_record(record, expect_tag, expect_record):
    from patient_side_GUI import validate_record
    tag, record_ns = validate_record(record)
    assert tag == expect_tag
    assert record_ns == expect_record


@pytest.mark.parametrize("name, expect_tag", [
    ('', 'Empty name'), ('   ', 'Empty name'), ('D Q', 'pass'),
    ('D. He', 'pass'), ('9i', 'Invalid name'), ('A*B', 'Invalid name')])
def test_validate_name(name, expect_tag):
    from patient_side_GUI import validate_name
    tag = validate_name(name)
    assert tag == expect_tag


@pytest.mark.parametrize("name, record, expect_tag, expect_record", [
    ("", "", 'Empty record', ''), ('', '  ', "Empty record", ''),
    ('David', 'ss', "Invalid record", ''), ("", "*^", "Invalid record", ''),
    ("/4D", " 2  5", "Invalid name", '25'),
    ("David.H", '3', 'pass', '3')])
def test_check_text_input(name, record, expect_tag, expect_record):
    from patient_side_GUI import check_text_input
    tag, record_ns = check_text_input(name, record)
    assert record_ns == expect_record
    assert tag == expect_tag


# @pytest.mark.parametrize("name, record, ecg_b64str, img_b64str, hr, warn", [
#     ("DavidH", 1, "FFAI=/", "UUUA9", "60", False),
#     ("", 2, "", "", "", True),
#     ("D.  Ward", 3, "", "UUUUU", "70", False)
#     ])
# def test_upload_info(name, record, ecg_b64str, img_b64str, hr, warn):
#     from patient_side_GUI import upload_info
#     # _, _, info = upload_info(name, record, ecg_b64str, img_b64str, hr)
#     info = upload_info(name, record, ecg_b64str, img_b64str, hr)
#     assert info["patient_name"] == name
#     assert info["patient_record_no"] == record
#     assert info["medical_img"] == img_b64str
#     assert info["ECG_img"] == ecg_b64str
#     assert info["heart_rate"] == hr
