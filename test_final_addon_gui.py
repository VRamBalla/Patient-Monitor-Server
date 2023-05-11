import base64

import pytest


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
    ({'2016-07-10 13:12:48': 13.56,
      '2015-08-27 14:52:38':
          'testing'},
     {'2015-08-27 14:52:38': 'testing', '2016-07-10 13:12:48': 13.56})
])
def test_sort_heart_rate_history_dict(history_dict, expect):
    from monitor_side_GUI import sort_history_dict
    answer = sort_history_dict(history_dict)

    assert answer == expect


@pytest.mark.parametrize('history_dict, expected_latest_value', [
    ({'2016-07-10 13:12:48': 88, '2017-08-27 14:52:38': 74, '2017-10-07 '
                                                            '06:29:22': 114,
      '2019-07-25 12:35:24': 111}, 111),
    ({'2016-07-10 13:12:48': 'leg88.jpg',
      '2017-08-27 14:52:38': 'leg74.jpg',
      '2017-10-07 06:29:22': 'leg114.jpg',
      '2019-07-25 12:35:24': 'leg111.jpg'},
     'leg111.jpg'),
    ({'2015-08-27 14:52:38': 49.58,
      '2016-07-10 13:12:48':
          'b64 str'}, 'b64 str')

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
    ({'2015-08-27 14:52:38': 29.58,
      '2016-07-10 13:12:48':
          [22, 23]}, '2016-07-10 13:12:48')

])
def test_latest_timestamp_in_history_dict(history_dict,
                                          expected_latest_timestamp):
    from monitor_side_GUI import latest_timestamp_in_history_dict
    result = latest_timestamp_in_history_dict(history_dict)
    assert result == expected_latest_timestamp
