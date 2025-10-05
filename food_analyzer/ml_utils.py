# food_analyzer/ml_utils.py
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image
import requests
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
# In the top section of ml_utils.py
import os # Add this import

USDA_API_KEY = os.environ.get("USDA_API_KEY")

print("--- LOADING ML_UTILS.PY (EfficientNetB0 + USDA API Version) ---")

# --- Nutrition API Configuration ---
# Your new API key has been added here.
USDA_API_KEY = "otKp7epXHTI0wXvInJ55CoHff8a12LCzCCZizGMh"
USDA_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# --- ML Model Loading (Your existing code) ---
MODEL_URL = "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_b0/classification/2"
IMAGE_NET_LABELS_URL = "https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt"

model = None
imagenet_labels = []

try:
    response = requests.get(IMAGE_NET_LABELS_URL)
    response.raise_for_status()
    labels_raw = response.text.split("\n")
    imagenet_labels = [label.strip() for label in labels_raw if label.strip()]
    if imagenet_labels and imagenet_labels[0].lower() == 'background':
        imagenet_labels = imagenet_labels[1:]
    print("✅ ImageNet labels loaded successfully.")
    
    model = hub.load(MODEL_URL)
    print("✅ TF-Hub model loaded successfully as a plain function.")
except Exception as e:
    print(f"❌ Error loading model or labels: {e}")

def preprocess_image(image_path, target_size=(224, 224)):
    img = Image.open(image_path).convert("RGB")
    img = img.resize(target_size)
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_food(image_path):
    if model is None or not imagenet_labels:
        return "Error: Model not loaded.", 0.0
    try:
        processed_image = preprocess_image(image_path)
        tensor_image = tf.convert_to_tensor(processed_image, dtype=tf.float32)
        predictions = model(tensor_image)
        logits = predictions[0]
        predicted_index = np.argmax(logits)
        predicted_name = imagenet_labels[predicted_index].replace("_", " ").title()
        probabilities = tf.nn.softmax(logits)
        confidence_score = float(probabilities[predicted_index])
        return predicted_name, confidence_score
    except Exception as e:
        print(f"Error during prediction: {e}")
        return "Prediction Error", 0.0

def get_nutrition_data(food_name):
    """
    Fetches nutrition data from the USDA FoodData Central API.
    """
    params = {
        'api_key': USDA_API_KEY,
        'query': food_name,
        'pageSize': 1, # Get the most likely match
    }
    try:
        response = requests.get(USDA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "foods" in data and data["foods"]:
            food_data = data["foods"][0]
            nutrients = {nutrient['nutrientName']: nutrient.get('value', 0) for nutrient in food_data.get('foodNutrients', [])}
            
            nutrition_info = {
                "name": food_data.get("description", food_name).title(),
                "calories": nutrients.get("Energy", 0),
                "protein_g": nutrients.get("Protein", 0),
                "carbs_g": nutrients.get("Carbohydrate, by difference", 0),
                "fat_g": nutrients.get("Total lipid (fat)", 0),
                "serving_qty": 100, # USDA data is typically per 100g
                "serving_unit": "g",
                "photo_url": None # USDA API does not provide photos
            }
            return nutrition_info
            
    except requests.exceptions.RequestException as e:
        print(f"USDA API error: {e}")
    return None

def handle_uploaded_image(image_file):
    """
    A helper function to manage the process of saving an image, predicting,
    getting nutrition, and cleaning up.
    """
    path = default_storage.save(f"tmp/{image_file.name}", ContentFile(image_file.read()))
    full_path = default_storage.path(path)
    
    try:
        # Run prediction on the saved image
        predicted_name, confidence = predict_food(full_path)
        
        # Get nutrition data for the prediction
        nutrition_info = None
        if predicted_name != "Prediction Error":
            nutrition_info = get_nutrition_data(predicted_name)
    finally:
        # Clean up the temporary file
        default_storage.delete(path)
    
    return predicted_name, confidence, nutrition_info