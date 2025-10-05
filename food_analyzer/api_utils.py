# food_analyzer/api_utils.py
import requests

# Your provided API key is here
API_KEY = "otKp7epXHTI0wXvInJ55CoHff8a12LCzCCZizGMh"
BASE_URL = "https://api.nal.usda.gov/fdc/v1"
NUTRIENT_IDS = {
    "Calories": 1008, "Protein": 1003, "Total lipid (fat)": 1004, "Carbohydrate, by difference": 1005
}

def get_nutrition_data(food_name):
    """Fetches nutrition data for a food from the USDA API."""
    search_params = {"query": food_name, "api_key": API_KEY, "dataType": ["Foundation", "SR Legacy"], "pageSize": 1}
    search_response = requests.get(f"{BASE_URL}/foods/search", params=search_params)

    if search_response.status_code != 200 or not search_response.json().get("foods"):
        return {"error": f"No nutrition data found for '{food_name}'. Try a more general term."}

    fdc_id = search_response.json()["foods"][0]["fdcId"]

    details_response = requests.get(f"{BASE_URL}/food/{fdc_id}", params={"api_key": API_KEY})
    if details_response.status_code != 200:
        return {"error": "Could not retrieve detailed nutrition data."}

    details_data = details_response.json()

    nutrition_info = {"food_name": details_data.get("description", food_name).title(), "serving_size": "per 100g", "nutrients": {}}
    api_nutrients = {n['nutrient']['id']: n for n in details_data.get("foodNutrients", [])}

    for nutrient_name, nutrient_id in NUTRIENT_IDS.items():
        if nutrient_id in api_nutrients:
            nutrient_data = api_nutrients[nutrient_id]
            value = nutrient_data.get("amount", 0)
            unit = nutrient_data.get("nutrient", {}).get("unitName", "").lower()
            nutrition_info["nutrients"][nutrient_name] = f"{value} {unit}"
        else:
            nutrition_info["nutrients"][nutrient_name] = "N/A"

    return nutrition_info