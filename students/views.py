from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import re
import uuid

from .student_data_storage import load_student_data, save_student_data
from .serializer import StudentSerializer

import requests
import json

# Function to validate email
def validate_email(email, student_data, update=False, current_email=None):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    
    if not re.match(email_regex, email):
        raise ValueError("Enter a valid email address.")
    
    # Check for email uniqueness
    for student in student_data.values():
        if student['email'] == email and (not update or student['email'] != current_email):
            raise ValueError("Email is already in use.")
    
    return email

# Function to validate name
def validate_name(name, student_data, update=False, current_name=None):
    if not name.strip():
        raise ValueError("Name cannot be empty.")
    
    if len(name) < 3:
        raise ValueError("Name must be at least 3 characters long.")
    
    # Check for name uniqueness
    for student in student_data.values():
        if student['name'] == name and (not update or student['name'] != current_name):
            raise ValueError("Name is already in use.")
    
    return name


@api_view(['POST'])
def create_student(request):
    # Extract the data from the request
    name = request.data.get("name")
    age = request.data.get("age")
    email = request.data.get("email")

    # Load current student data from the file
    student_data = load_student_data()
    # print(student_data)

    # Validation
    try:
        name = validate_name(name, student_data)  # Pass student_data as argument
        email = validate_email(email, student_data)  # Pass student_data as argument
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Generate a unique student ID
    student_id = str(uuid.uuid4())  # Generate a unique ID for each student
    
    # Create student object
    student = {
        "id": student_id,
        "name": name,
        "age": age,
        "email": email
    }
    
    # Add the new student to the in-memory data
    student_data[student_id] = student
    
    # Save the updated student data to the file
    save_student_data(student_data)

    return Response(student, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_all_students(request):
    # Load all student data from the file
    student_data = load_student_data()

    # Serialize the data (many=True to serialize a list of students)
    serializer = StudentSerializer(student_data.values(), many=True)

    # Return the serialized data as JSON response
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_student(request, id):
    # Load student data from the file
    student_data = load_student_data()

    # print(f"Received ID: {id}")
    # print(f"Student Data: {student_data}")

    # Try to find the student by ID
    student = student_data.get(str(id))  # Ensure id is treated as a string if needed

    if not student:
        # Return 404 if the student is not found
        return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Serialize the data (many=True to serialize a list of students)
    serializer = StudentSerializer(student)

    # Return the student data directly as a response
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def update_student(request, id):
    # Ensure the 'id' in the URL matches the 'id' in the request body (optional check)
    body_id = request.data.get('id')

    if body_id != str(id):  # Check if the ID in the URL matches the one in the body
        return Response({"error": "ID mismatch between URL and body."}, status=status.HTTP_400_BAD_REQUEST)

    # Load current student data from the file
    student_data = load_student_data()

    # Check if the student exists in the in-memory store
    if str(id) not in student_data:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get the existing student
    student = student_data[str(id)]

    # Validate and update fields
    try:
        name = request.data.get("name", student["name"])  # Get new name or keep existing
        email = request.data.get("email", student["email"])  # Get new email or keep existing
        age = request.data.get("age", student["age"])  # Get new age or keep existing

        # Pass student_data to the validation functions
        name = validate_name(name, student_data, update=True, current_name=student["name"])
        email = validate_email(email, student_data, update=True, current_email=student["email"])

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Update the student data
    student_data[str(id)] = {
        "id": str(id),
        "name": name,
        "email": email,
        "age": age
    }

    # Save the updated student data back to the file
    save_student_data(student_data)

    # Return the updated student data
    return Response(student_data[str(id)], status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_student(request, id):
    # Load current student data from the file
    student_data = load_student_data()

    # Check if the student exists in the in-memory store
    if str(id) not in student_data:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    # Delete the student from the in-memory store
    del student_data[str(id)]

    # Save the updated student data back to the file
    save_student_data(student_data)

    # Return a response confirming the deletion
    return Response({"message": "Student deleted."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def generate_student_summary(request, id):
    # Load student data from the file
    student_data = load_student_data()

    # Check if the student exists in the in-memory store
    if str(id) not in student_data:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get the student data
    student = student_data[str(id)]

    # Serialize the student data
    serializer = StudentSerializer(student)
    student_data = serializer.data

    # Extract important student details
    name = student_data.get('name')
    age = student_data.get('age')
    email = student_data.get('email')
    skills = student_data.get('skills', [])
    achievements = student_data.get('achievements', [])
    hobbies = student_data.get('hobbies', [])

    # Define the Ollama API endpoint
    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }

    # Create a more compelling and story-like prompt
    prompt = f"""
    Write a detailed and engaging story about the student profile. Include the following information:
    - Name: {name}
    - Age: {age}
    - Email: {email}
    
    Tell a story about the student’s educational journey, highlighting:
    1. Their academic achievements and accomplishments (e.g., degrees, awards).
    2. Skills they have gained (mention any programming languages, tools, or certifications).
    3. Hobbies and personal interests (e.g., activities, passions outside of academics).
    
    Make sure the summary feels personalized and interesting, as if you are telling the story of a person’s journey.
    """

    # Send the formatted request data to Ollama API
    data = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }

    # Make the POST request to Ollama
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))

        # Handle Ollama response
        if response.status_code == 200:
            response_text = response.text
            data = json.loads(response_text)
            actual_response = data.get("response")
            return Response({"summary": actual_response}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to generate summary.", "details": response.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Request failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def delete_List_student(request):

    data= request.data

    student_data = load_student_data()
    
    deleted_student=[]

    for i in data:
        if student_data.get(i) is not None:
            deleted_student.append(student_data[i])
            del student_data[i]

    save_student_data()

    return deleted_student

    


    


