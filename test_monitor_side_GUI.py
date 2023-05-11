import base64
import pytest
from PIL import Image


@pytest.mark.parametrize('input_dict, expected_output_dict', [
    ({'heart_rate_history': {}, 'medical_filename_history': {'2015-03-17 '
                                                             '10:34:28':
                                                                 "leg.jpg"}},
     {'heart_rate_history': '(No data yet)',
      'medical_filename_history': {
          '2015-03-17 '
          '10:34:28':
              "leg.jpg"}}),
    ({'heart_rate_history': {'2015-03-17 10:34:28': 120},
      'medical_filename_history': {}},
     {'heart_rate_history': {'2015-03-17 10:34:28': 120},
      'medical_filename_history': '(No data yet)'}),
    ({'heart_rate_history': {}, 'medical_filename_history': {}},
     {'heart_rate_history': '(No data yet)',
      'medical_filename_history': '(No data yet)'}),
    ({'heart_rate_history': {'2015-03-17 10:34:28': 120},
      'medical_filename_history': {'2015-03-17 10:34:28': "leg.jpg"}},
     {'heart_rate_history': {'2015-03-17 10:34:28': 120},
      'medical_filename_history': {'2015-03-17 10:34:28': "leg.jpg"}})
])
def test_organize_patient_info_for_GUI(input_dict, expected_output_dict):
    from monitor_side_GUI import organize_patient_info_for_GUI
    result_dict = organize_patient_info_for_GUI(input_dict)
    assert result_dict == input_dict


@pytest.mark.parametrize('history_dict, expect', [
    ({'2016-07-10 13:12:48': 88, '2017-08-27 14:52:38': 74, '2017-10-07 '
                                                            '06:29:22': 114,
      '2019-07-25 12:35:24': 111}, {'2016-07-10 13:12:48': 88,
                                    '2017-08-27 14:52:38': 74,
                                    '2017-10-07 06:29:22': 114,
                                    '2019-07-25 12:35:24': 111}),
    ({'2019-07-25 12:35:24': 111, '2017-10-07 06:29:22': 114, '2017-08-27 '
                                                              '14:52:38': 74,
      '2016-07-10 13:12:48': 88}, {'2016-07-10 13:12:48': 88,
                                   '2017-08-27 14:52:38': 74,
                                   '2017-10-07 06:29:22': 114,
                                   '2019-07-25 12:35:24': 111}),
    ({'2019-07-25 12:35:24': 111}, {'2019-07-25 12:35:24': 111}),
    ({'2016-07-10 13:12:48': 'leg88.jpg', '2017-08-27 14:52:38': 'leg74.jpg',
      '2017-10-07 '
      '06:29:22':
          'leg114.jpg',
      '2019-07-25 12:35:24': 'leg111.jpg'},
     {'2016-07-10 13:12:48': 'leg88.jpg',
      '2017-08-27 14:52:38': 'leg74.jpg',
      '2017-10-07 06:29:22': 'leg114.jpg',
      '2019-07-25 12:35:24': 'leg111.jpg'}),
    ({'2016-07-10 13:12:48': '/9j/4AAQSkZJRgABAQEAwADAAAD/2wBDAA'
                             'gGBgcGB'
                             'QgHBwcJCQgKDBQNDAsL'
                             'DBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcp'
                             'LDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwL'
                             'DBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIy'
                             'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
                             'yMjIyMjIyMjL/wAARCAAJAAkDAREAAhEBAxE'
                             'B/8QAFQABAQAAAAAAAAAAAAAAAAAABwT/xA'
                             'AfEAABAwMFAAAAAAAAAAAAAAABAAQRAgUHEj'
                             'RSccH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
                             'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQAC'
                             'EQMRAD8Akx03Di4EkTogoFmaeKA0xnvHHX'
                             'iBKQf/2Q==',
      '2015-08-27 14:52:38':
          '/9j/4AAQSkZJRgABAQEAwADAAAD/2wBDAA'
          'gGBgcGB'
          'QgHBwcJCQgKDBQNDAsL'
          'DBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcp'
          'LDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwL'
          'DBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIy'
          'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
          'yMjIyMjIyMjL/wAARCAAJAAkDAREAAhEBAxE'
          'B/8QAFQABAQAAAAAAAAAAAAAAAAAABwT/xA'
          'AfEAABAwMFAAAAAAAAAAAAAAABAAQRAgUHEj'
          'RSccH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
          'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQAC'
          'EQMRAD8Akx03Di4EkTogoFmaeKA0xnvHHX'
          'iBKQf/2Q=='},
     {'2015-08-27 14:52:38': '/9j/4AAQSkZJRgABAQEAwADAAAD/2wBDAA'
                             'gGBgcGB'
                             'QgHBwcJCQgKDBQNDAsL'
                             'DBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcp'
                             'LDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwL'
                             'DBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIy'
                             'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
                             'yMjIyMjIyMjL/wAARCAAJAAkDAREAAhEBAxE'
                             'B/8QAFQABAQAAAAAAAAAAAAAAAAAABwT/xA'
                             'AfEAABAwMFAAAAAAAAAAAAAAABAAQRAgUHEj'
                             'RSccH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
                             'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQAC'
                             'EQMRAD8Akx03Di4EkTogoFmaeKA0xnvHHX'
                             'iBKQf/2Q==', '2016-07-10 13:12:48':
          '/9j/4AAQSkZJRgABAQEAwADAAAD/2wBDAA'
          'gGBgcGB'
          'QgHBwcJCQgKDBQNDAsL'
          'DBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcp'
          'LDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwL'
          'DBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIy'
          'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
          'yMjIyMjIyMjL/wAARCAAJAAkDAREAAhEBAxE'
          'B/8QAFQABAQAAAAAAAAAAAAAAAAAABwT/xA'
          'AfEAABAwMFAAAAAAAAAAAAAAABAAQRAgUHEj'
          'RSccH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
          'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQAC'
          'EQMRAD8Akx03Di4EkTogoFmaeKA0xnvHHX'
          'iBKQf/2Q=='})
])
def test_sort_history_dict(history_dict, expect):
    from monitor_side_GUI import sort_history_dict
    answer = sort_history_dict(history_dict)

    assert answer == expect


@pytest.mark.parametrize('history_dict, expected_latest_value', [
    ({'2016-07-10 13:12:48': 88, '2017-08-27 14:52:38': 74, '2017-10-07 '
                                                            '06:29:22': 114,
      '2019-07-25 12:35:24': 111}, 111),
    ({'2016-07-10 13:12:48': 88, '2017-10-07 06:29:22': 114,
      '2019-07-25 12:35:24': 111, '2017-08-27 14:52:38': 74}, 111),
    ({'2016-07-10 13:12:48': 'leg88.jpg',
      '2017-08-27 14:52:38': 'leg74.jpg',
      '2017-10-07 06:29:22': 'leg114.jpg',
      '2019-07-25 12:35:24': 'leg111.jpg'},
     'leg111.jpg'),
    ({'2019-07-25 12:35:24': 'leg111.jpg', '2016-07-10 13:12:48': 'leg88.jpg',
      '2017-08-27 14:52:38': 'leg74.jpg',
      '2017-10-07 06:29:22': 'leg114.jpg'
      },
     'leg111.jpg'),
    ({'2015-08-27 14:52:38': '/9j/4AAQSkZJRgABAQEAwADAAAD/2wBDAA'
                             'gGBgcGB'
                             'QgHBwcJCQgKDBQNDAsL'
                             'DBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcp'
                             'LDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwL'
                             'DBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIy'
                             'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
                             'yMjIyMjIyMjL/wAARCAAJAAkDAREAAhEBAxE'
                             'B/8QAFQABAQAAAAAAAAAAAAAAAAAABwT/xA'
                             'AfEAABAwMFAAAAAAAAAAAAAAABAAQRAgUHEj'
                             'RSccH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
                             'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQAC'
                             'EQMRAD8Akx03Di4EkTogoFmaeKA0xnvHHX'
                             'iBKQf/2Q==',
      '2016-07-10 13:12:48':
          '/9j/4AAQSkZJRgABAQEAwADAAAD/2wBDAA'
          'gGBgcGB'
          'QgHBwcJCQgKDBQNDAsL'
          'DBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcp'
          'LDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwL'
          'DBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIy'
          'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
          'yMjIyMjIyMjL/wAARCAAJAAkDAREAAhEBAxE'
          'B/8QAFQABAQAAAAAAAAAAAAAAAAAABwT/xA'
          'AfEAABAwMFAAAAAAAAAAAAAAABAAQRAgUHEj'
          'RSccH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
          'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQAC'
          'EQMRAD8Akx03Di4EkTogoFmaeKA0xnvHHX'
          'iBKQf/2Q=='}, '/9j/4AAQSkZJRgABAQEAwADAA'
                         'AD/2wBDAA'
                         'gGBgcGB'
                         'QgHBwcJCQgKDBQNDAsL'
                         'DBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcp'
                         'LDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwL'
                         'DBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIy'
                         'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
                         'yMjIyMjIyMjL/wAARCAAJAAkDAREAAhEBAxE'
                         'B/8QAFQABAQAAAAAAAAAAAAAAAAAABwT/xA'
                         'AfEAABAwMFAAAAAAAAAAAAAAABAAQRAgUHEj'
                         'RSccH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
                         'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQAC'
                         'EQMRAD8Akx03Di4EkTogoFmaeKA0xnvHHX'
                         'iBKQf/2Q==')

])
def test_latest_value_in_history_dict(history_dict, expected_latest_value):
    from monitor_side_GUI import latest_value_in_history_dict
    result = latest_value_in_history_dict(history_dict)
    assert result == expected_latest_value


@pytest.mark.parametrize('history_dict, expected_latest_timestamp', [
    ({'2016-07-10 13:12:48': 88, '2017-08-27 14:52:38': 74, '2017-10-07 '
                                                            '06:29:22': 114,
      '2019-07-25 12:35:24': 111}, '2019-07-25 12:35:24'),
    ({'2016-07-10 13:12:48': 'leg88.jpg',
      '2017-08-27 14:52:38': 'leg74.jpg',
      '2017-10-07 06:29:22': 'leg114.jpg',
      '2019-07-25 12:35:24': 'leg111.jpg'},
     '2019-07-25 12:35:24'),
    ({'2015-08-27 14:52:38': '/9j/4AAQSkZJRgABAQEAwADAAAD/2wBDAA'
                             'gGBgcGB'
                             'QgHBwcJCQgKDBQNDAsL'
                             'DBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcp'
                             'LDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwL'
                             'DBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIy'
                             'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
                             'yMjIyMjIyMjL/wAARCAAJAAkDAREAAhEBAxE'
                             'B/8QAFQABAQAAAAAAAAAAAAAAAAAABwT/xA'
                             'AfEAABAwMFAAAAAAAAAAAAAAABAAQRAgUHEj'
                             'RSccH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
                             'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQAC'
                             'EQMRAD8Akx03Di4EkTogoFmaeKA0xnvHHX'
                             'iBKQf/2Q==',
      '2016-07-10 13:12:48':
          '/9j/4AAQSkZJRgABAQEAwADAAAD/2wBDAA'
          'gGBgcGB'
          'QgHBwcJCQgKDBQNDAsL'
          'DBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcp'
          'LDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwL'
          'DBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIy'
          'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
          'yMjIyMjIyMjL/wAARCAAJAAkDAREAAhEBAxE'
          'B/8QAFQABAQAAAAAAAAAAAAAAAAAABwT/xA'
          'AfEAABAwMFAAAAAAAAAAAAAAABAAQRAgUHEj'
          'RSccH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
          'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQAC'
          'EQMRAD8Akx03Di4EkTogoFmaeKA0xnvHHX'
          'iBKQf/2Q=='}, '2016-07-10 13:12:48')

])
def test_latest_timestamp_in_history_dict(history_dict,
                                          expected_latest_timestamp):
    from monitor_side_GUI import latest_timestamp_in_history_dict
    result = latest_timestamp_in_history_dict(history_dict)
    assert result == expected_latest_timestamp


@pytest.mark.parametrize('file_direct, expect_first_five_ndarray', [
    ('./test_images/med_img.jpg', [[60, 60, 60],
                                   [67, 67, 67],
                                   [71, 71, 71],
                                   [83, 83, 83],
                                   [105, 105, 105]]),
    ('./test_images/test_image.jpg', [[68, 115, 197],
                                      [68, 115, 197],
                                      [68, 115, 197],
                                      [68, 115, 197],
                                      [68, 115, 197]])

])
def test_convert_b64_str_to_ndarray(file_direct, expect_first_five_ndarray):
    from monitor_side_GUI import convert_b64_str_to_ndarray
    with open(file_direct, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding='utf-8')

    result_ndarray = convert_b64_str_to_ndarray(b64_string)[0][0:5]
    assert (result_ndarray == expect_first_five_ndarray).all


@pytest.mark.parametrize('original_file_direct', [
    ('./test_images/med_img.jpg'),
    ('./test_images/test_image.jpg')
])
def test_b64_str_to_img_download(original_file_direct):
    from monitor_side_GUI import b64_str_to_img_download
    import filecmp
    import os

    with open(original_file_direct, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding='utf-8')

    new_file_direct = './test_images/test_image_output.jpg'
    b64_str_to_img_download(b64_string, new_file_direct)
    answer = filecmp.cmp(original_file_direct,
                         new_file_direct)
    os.remove(new_file_direct)
    assert answer is True


@pytest.mark.parametrize('input_str, expected_answer',
                         [('123', True),
                          ('0123', True),
                          ('p123', False),
                          ('1p23', False),
                          ('123p', False),
                          ('p1p23', False),
                          ('p123p', False),
                          ('1p23p', False),
                          ('p1p23p', False)]
                         )
def test_judge_int_str(input_str, expected_answer):
    from monitor_side_GUI import judge_int_str
    answer = judge_int_str(input_str)
    assert answer == expected_answer


def test_resize_image():
    from monitor_side_GUI import convert_b64_str_to_ndarray, resize_image
    img_ndarray = convert_b64_str_to_ndarray(
        '/9j/4AAQSkZJRgABAQEAwADAAAD'
        '/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxw'
        'cKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIy'
        'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAJ'
        'AAkDAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAABwT/xAAfEAABAwMFAAAA'
        'AAAAAAAAAAABAAQRAgUHEjRSccH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBA'
        'AAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8Akx03Di4EkTogoFmaeKA0xnvHH'
        'XiBKQf/2Q==')  # This is a square image
    image_obj = Image.fromarray(img_ndarray)
    resized_image_obj = resize_image(
        image_obj)
    x, y = resized_image_obj.size
    print(x, y)
    assert x == 150
    assert y == 150
