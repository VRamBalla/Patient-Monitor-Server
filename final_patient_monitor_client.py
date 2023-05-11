import requests

# **************************Junqi Lu starts**************************
url = 'http://127.0.0.1:5000'

# Test the server status
r = requests.get(url + "/")
print(r.status_code)
print(r.text)

# Test the database connection status
r = requests.get(url + "/api/monitor/database_connect_status")
print(r.status_code)
print(r.json())

# Test the database content--whether it is empty
r = requests.get(url + "/api/monitor/all_med_number")
print(r.status_code)
print(r.json())  # ['Database is empty. Add in data from patient GUI first']
# is the database is empty

# Test the function to find out the patient data dict by a given record number
r = requests.get(url + "/api/monitor/patient_info/10")
print(r.status_code)
print(r.json())  # {} if a given record number doesn't exist in the database

# **************************Junqi Lu ends**************************

# **************************Ramana Balla starts**************************
# **************************Ramana Balla ends**************************

# **************************Ziwei He starts**************************
# **************************Ziwei He ends**************************
