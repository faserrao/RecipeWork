import streamlit as st
import pandas as pd
import requests

def fetch_ingredient_category(ingredient_name):
    """Dynamically fetch ingredient category using the USDA FoodData Central API."""
    api_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={ingredient_name}&api_key=DEMO_KEY"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if "foods" in data and len(data["foods"]) > 0:
                food_category = data["foods"][0].get("foodCategory", "Unknown")
                return "Dry" if "grain" in food_category.lower() or "powder" in food_category.lower() else "Wet"
    except Exception as e:
        print(f"Error fetching ingredient category: {e}")
    return "Unknown"

def categorize_ingredient(ingredient_name, unit):
    """Use API lookup first; fallback to unit-based categorization."""
    dry_ingredients = ["flour", "sugar", "salt", "baking powder", "cocoa powder", "cornstarch", "oats", "breadcrumbs"]
    wet_ingredients = ["milk", "water", "oil", "juice", "honey", "vinegar", "syrup"]
    
    if any(item in ingredient_name.lower() for item in dry_ingredients):
        return "Dry"
    elif any(item in ingredient_name.lower() for item in wet_ingredients):
        return "Wet"
    
    category = fetch_ingredient_category(ingredient_name)
    if category != "Unknown":
        return category
    
    return "Wet" if unit in ["gallon", "quart", "pint", "cup", "fluid ounce", "liter", "milliliter"] else "Dry"

conversions = {
    "gallon": {"quart": 4, "pint": 8, "cup": 16, "fluid ounce": 128, "tablespoon": 256, "teaspoon": 768, "liter": 3.785, "milliliter": 3785},
    "quart": {"gallon": 1/4, "pint": 2, "cup": 4, "fluid ounce": 32, "tablespoon": 64, "teaspoon": 192, "liter": 0.946, "milliliter": 946},
    "pint": {"gallon": 1/8, "quart": 1/2, "cup": 2, "fluid ounce": 16, "tablespoon": 32, "teaspoon": 96, "liter": 0.473, "milliliter": 473},
    "cup": {"gallon": 1/16, "quart": 1/4, "pint": 1/2, "fluid ounce": 8, "tablespoon": 16, "teaspoon": 48, "liter": 0.24, "milliliter": 237},
    "fluid ounce": {"gallon": 1/128, "quart": 1/32, "pint": 1/16, "cup": 1/8, "tablespoon": 2, "teaspoon": 6, "milliliter": 29.57},
    "tablespoon": {"cup": 1/16, "teaspoon": 3, "milliliter": 14.79},
    "teaspoon": {"cup": 1/48, "tablespoon": 1/3, "milliliter": 4.93},
    "gram": {"milligram": 1000, "ounce": 0.0353, "pound": 0.0022, "teaspoon": 0.2, "tablespoon": 0.067},
    "milligram": {"gram": 0.001, "teaspoon": 0.0002, "tablespoon": 0.00007},
    "ounce": {"gram": 28.35, "pound": 1/16, "teaspoon": 6, "tablespoon": 2},
    "pound": {"ounce": 16, "gram": 453.592, "teaspoon": 96, "tablespoon": 32},
}



def convert_units(amount, unit, cost_per_unit, cost_unit):
    if unit != cost_unit and cost_unit in conversions and unit in conversions[cost_unit]:
        conversion_factor = conversions[cost_unit].get(unit, 1)
        adjusted_cost_per_unit = cost_per_unit / conversion_factor
    else:
        adjusted_cost_per_unit = cost_per_unit
    
    total_cost = adjusted_cost_per_unit * amount
    
    converted_values = {
        "Ingredient": "",
        "Category": "",
        "Amount": amount,
        "Unit": unit,
        "Total Cost ($)": round(total_cost, 2),
        "Unit for Cost": cost_unit,
    }
    
    if unit in conversions:
        for new_unit, factor in conversions[unit].items():
            converted_values[new_unit] = round(amount * factor, 2)
            converted_values[f"Cost per {new_unit} ($)"] = round(adjusted_cost_per_unit / factor, 2) if factor > 0 else 0
    
    converted_values[f"Cost per {cost_unit} ($)"] = round(adjusted_cost_per_unit, 2)
    
    return converted_values

st.title("Ingredient Measurement Converter")

if "ingredients" not in st.session_state:
    st.session_state.ingredients = []

with st.form("ingredient_form"):
    ingredient = st.text_input("Ingredient Name")
    amount = st.number_input("Amount", min_value=0.01, step=0.01)
    unit = st.selectbox("Unit", list(conversions.keys()))
    cost_per_unit = st.number_input("Cost per Unit ($)", min_value=0.0, step=0.01)
    cost_unit = st.selectbox("Unit for Cost", list(conversions.keys()))
    submitted = st.form_submit_button("Add Ingredient")
    
    if submitted and ingredient:
        converted_data = convert_units(amount, unit, cost_per_unit, cost_unit)
        converted_data["Ingredient"] = ingredient
        converted_data["Category"] = categorize_ingredient(ingredient, unit)
        st.session_state.ingredients.append(converted_data)

if st.session_state.ingredients:
    df = pd.DataFrame(st.session_state.ingredients)
    cost_columns = [col for col in df.columns if "Cost per" in col]
    primary_columns = ["Ingredient", "Category", "Amount", "Unit", "Total Cost ($)", "Unit for Cost"]
    other_columns = [col for col in df.columns if col not in primary_columns + cost_columns]
    df = df[primary_columns + other_columns + cost_columns]
    st.dataframe(df)
