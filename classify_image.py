from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tensorflow.keras.applications import densenet
from tensorflow.keras.applications.densenet import preprocess_input, decode_predictions
import numpy as np
from PIL import Image
from contextlib import asynccontextmanager
import base64
import io


# Define the input schema for the API
class ImagePayload(BaseModel):
    image: str  # Base64 encoded image data


# Load the pre-trained DenseNet121 model on startup
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    # Load the model during startup
    model = densenet.DenseNet121(
        weights="./densenet121_weights_tf_dim_ordering_tf_kernels.h5")  # Load pre-trained weights
    print("DenseNet121 model loaded!")
    try:
        yield
    finally:
        # Cleanup
        model = None
        print("DenseNet121 model unloaded!")


# Initialize the FastAPI app
app = FastAPI(lifespan=lifespan)


# Define the image preprocessing function
def preprocess_image(image_data):
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image = image.resize((224, 224))  # Resize to match DenseNet input size
    image_array = np.array(image)
    image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
    return preprocess_input(image_array)


# Define the /predict endpoint
@app.post("/predict")
async def predict(payload: ImagePayload):
    try:
        # Decode the base64 image
        image_data = base64.b64decode(payload.image)

        # Preprocess the image
        input_tensor = preprocess_image(image_data)

        # Make prediction
        predictions = model.predict(input_tensor)

        # Decode the predictions to human-readable labels
        decoded_predictions = decode_predictions(predictions, top=1)[0]  # Get top prediction
        response_label = decoded_predictions[0][1]  # Get the class label
        return {"response": response_label}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing the image: {str(e)}")
