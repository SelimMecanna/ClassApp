import base64
import pytest
from fastapi.testclient import TestClient
from classify_image import *  # Replace with your script's name


# Helper function to load a sample image and encode it to Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# List of test images with their expected predictions
test_images = [
    {"path": "./Test_Images/cat.jpg", "expected_response": "Egyptian_cat"},
    {"path": "./Test_Images/dog.jpg", "expected_response": "dingo"},
    {"path": "./Test_Images/hen.jpg", "expected_response": "hen"},
    {"path": "./Test_Images/owl.png", "expected_response": "great_grey_owl"},
    {"path": "./Test_Images/panda.jpeg", "expected_response": "giant_panda"},
]


# Test: Successful predictions for multiple images
@pytest.mark.parametrize("image_data", test_images)
def test_predict_multiple_images(image_data):
    with TestClient(app) as client:
        base64_image = encode_image_to_base64(image_data["path"])  # Encode each image
        response = client.post("/predict", json={"image": base64_image})
        assert response.status_code == 200
        assert "response" in response.json()  # Check if "response" is in output
        assert response.json()["response"] == image_data["expected_response"]  # Verify prediction


# List of invalid test images with their expected predictions
invalid_images = [
    {"image": "/9j/4AAQSkZJRgABAQAAAQABAAD/2",
     "error_message": "Error processing the image: Invalid base64-encoded string: number of data characters (29) "
                      "cannot be 1 more than a multiple of 4"},
    {"image": "/9j/4AAQSkZJRgABAQAAAQABAAD", "error_message": "Error processing the image: Incorrect padding"},
    {"image": "/9j/4AAQSkZJRgABAQAAAQABAA", "error_message": "Error processing the image: Incorrect padding"},
]


# Test: Invalid images
@pytest.mark.parametrize("image_data", invalid_images)
def test_predict_invalid_input(image_data):
    with TestClient(app) as client:
        response = client.post("/predict", json={"image": image_data["image"]})
        assert response.status_code == 400
        assert image_data["error_message"] in response.json()["detail"]


invalid_inputs = [
    {"image": 30, "error_message": "Input should be a valid string"},
    {"image": True, "error_message": "Input should be a valid string"},
    {"image": [20, 'sas'], "error_message": "Input should be a valid string"},
]


# Test: Invalid input type
@pytest.mark.parametrize("image_data", invalid_inputs)
def test_correct_input_type(image_data):
    with TestClient(app) as client:
        response = client.post("/predict", json={"image": image_data["image"]})
        assert image_data["error_message"] in response.json()["detail"][0]["msg"]
