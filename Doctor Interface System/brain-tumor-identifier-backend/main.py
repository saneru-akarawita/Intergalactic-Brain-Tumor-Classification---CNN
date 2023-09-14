from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List

import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import matplotlib.pyplot as plt

# List of interior types
BRAIN_TUMOR_TYPES = ['glioma', 'meningioma', 'notumor', 'pituitary']

# File upload directory
UPLOAD_DIRECTORY = "/uploads"

# Load the trained model
model = load_model('trained_model_for_brain_tumor.h5')


def analyse__and_predict(image_file: str):
    # image_file = 'test.jpg'
    image_size = (150, 150)

    # Preprocess the test image
    processed_image = preprocess_image(image_file, image_size)

    # Make prediction
    prediction = model.predict(processed_image)
    predicted_class = np.argmax(prediction, axis=1)[0]
    predicted_type = BRAIN_TUMOR_TYPES[predicted_class]

    # Get probabilities for all interior types
    probabilities = prediction[0]
    
    prediction_result = {
        "type": predicted_type,
        "probabilities": {
            "glioma": 0,
            "meningioma": 0,
            "notumor": 0,
            "pituitary": 0,
        },
    }
    
    for brain_tumor_type, probability in zip(BRAIN_TUMOR_TYPES, probabilities):
        # print(f'\t{brain_tumor_type}: {probability * 100:.2f}%')
        prediction_result["probabilities"][brain_tumor_type] = probability * 100
        
    return prediction_result
    


# Function to preprocess the image
def preprocess_image(image_path, image_size):
    img = Image.open(image_path)
    img = img.convert('RGB')
    img = img.resize(image_size)
    img_array = np.array(img)
    img_array = img_array.astype(np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


app = FastAPI()
origins = [
    "http://localhost:3000",  # Replace with your frontend's URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predictions-for-uploaded-image")
async def get_predictions_for_image(file: UploadFile):
    
    # if no image, return 400 error
    if not file:
        return JSONResponse(status_code=400, content={"message": "No image uploaded"})
    
    
    # if uploads directory does not exist, create it
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
        
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    
    # Save the file to the temporary directory
    with open(file_path, "wb") as f:
        f.write(file.file.read())
        
    predictions = analyse__and_predict(file_path)
    
    # delete the file
    os.remove(file_path)
    
    return predictions