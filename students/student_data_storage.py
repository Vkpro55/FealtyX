# student_data_storage.py

import json
import os

# Get the absolute path to the root directory (where manage.py is located)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the file where the student data will be stored
DATA_FILE_PATH = os.path.join(BASE_DIR, 'students_data.json')


def load_student_data():
    try:
        with open('students_data.json', 'r') as file:
            # Attempt to load the JSON data
            data = json.load(file)
            return data
            
    except json.JSONDecodeError:
        # If the file is empty or not valid JSON, return an empty dictionary
        return {}
        
    except FileNotFoundError:
        # If the file doesn't exist, return an empty dictionary
        return {}


# Helper function to save data to the file
def save_student_data(data):
    with open(DATA_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

