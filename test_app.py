import os
import tempfile
from app import app
import pandas as pd

def run_tests():
    app.config['TESTING'] = True
    client = app.test_client()

    print("Running Application Tests...")

    # 1. Test Login & Dashboard
    response = client.post('/login', data={'username': 'test_user'}, follow_redirects=True)
    if response.status_code != 200 or b'test_user' not in response.data:
        print("FAIL: Login failed")
        return
    print("PASS: Login")

    # 2. Test Single File Upload
    # Create sample CSV
    csv_data = "col1,col2\n1,A\n2,B"
    data = {'file': (open(file_path("test.csv", csv_data), 'rb'), 'test.csv')}
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    if response.status_code != 200 or b'col1' not in response.data:
        print("FAIL: Single upload failed")
        return
    print("PASS: Single File Upload")

    # 3. Test Multi File Upload & Schema Alignment
    # We will upload 2 files and trigger schema align
    data = {
        'file': [
            (open(file_path("test1.csv", "id,name\n1,alice"), 'rb'), 'test1.csv'),
            (open(file_path("test2.csv", "ID,Name\n2,bob"), 'rb'), 'test2.csv')
        ]
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    if response.status_code != 200 or b'Dataset 2' not in response.data:
        print("FAIL: Multi upload / Schema alignment initiation failed")
        return
    print("PASS: Multi-file Upload & Schema Alignment Trigger")

    # Submit alignment
    align_data = {
        'map_1_ID': 'id',
        'map_1_Name': 'name'
    }
    response = client.post('/schema_align', data=align_data, follow_redirects=True)
    if response.status_code != 200 or 'column_select' not in response.request.path and b'<table' not in response.data:
        print("FAIL: Schema alignment execution failed")
        return
    print("PASS: Schema Alignment Processing")

    print("ALL TESTS PASSED SUCCESSFULLY!")

def file_path(name, content):
    path = os.path.join(tempfile.gettempdir(), name)
    with open(path, 'w') as f:
        f.write(content)
    return path

if __name__ == "__main__":
    run_tests()
