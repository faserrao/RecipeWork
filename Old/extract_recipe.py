import argparse
import requests
from recipe_scrapers import scrape_html
import pandas as pd
from fractions import Fraction
import unicodedata

# Density dictionary (grams per milliliter) for common ingredients
DENSITY_DICT = {
    'all-purpose flour': 0.593,
    'sugar': 0.845,
    'brown sugar': 0.721,
    'butter': 0.911,
    'milk': 1.03,
    'water': 1.0,
    'honey': 1.42,
    'olive oil': 0.91,
    'salt': 1.2,
    'ricotta cheese': 1.03,  # Approximate density
    # Add more ingredients and their densities as needed
}

# Conversion factors from common units to grams or milliliters
UNIT_CONVERSIONS = {
    'teaspoon': 4.92892,
    'tsp': 4.92892,
    'teaspoons': 4.92892,
    'tablespoon': 14.7868,
    'tbsp': 14.7868,
    'tablespoons': 14.7868,
    'cup': 240.0,
    'cups': 240.0,
    'pint': 473.176,
    'pints': 473.176,
    'quart': 946.353,
    'quarts': 946.353,
    'gallon': 3785.41,
    'gallons': 3785.41,
    'ml': 1.0,
    'milliliter': 1.0,
    'milliliters': 1.0,
    'l': 1000.0,
    'liter': 1000.0,
    'liters': 1000.0,
    'fl oz': 29.5735,
    'fluid ounce': 29.5735,
    'fluid ounces': 29.5735,
    'ounce': 28.3495,
    'ounces': 28.3495,
    'oz': 28.3495,
    'pound': 453.592,
    'pounds': 453.592,
    'lb': 453.592,
    'lbs': 453.592,
    'gram': 1.0,
    'grams': 1.0,
    'g': 1.0,
    'kilogram': 1000.0,
    'kilograms': 1000.0,
    'kg': 1000.0,
    # Add more units as needed
}

def get_args():
    parser = argparse.ArgumentParser(description="Extract recipe ingredients from a website and save to an Excel file.")
    parser.add_argument("url", help="The URL of the recipe page.")
    return parser.parse_args()

def extract_recipe(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    html = response.text
    scraper = scrape_html(html, org_url=url)
    title = scraper.title()
    ingredients = scraper.ingredients()
    return title, ingredients

def parse_quantity(quantity_str):
    """
    Convert a string representing a quantity (e.g., '½', '1/4', '1 1/2') to a float.
    """
    try:
        # Normalize unicode fractions (e.g., '½' to '1/2')
        quantity_str = unicodedata.normalize('NFKC', quantity_str)
        # Handle mixed numbers (e.g., '1 1/2')
        if ' ' in quantity_str:
            whole, frac = quantity_str.split()
            return float(whole) + float(Fraction(frac))
        else:
            return float(Fraction(quantity_str))
    except ValueError:
        return None

def parse_ingredient(ingredient):
    """
    Parse an ingredient string into quantity, unit, and ingredient name.
    """
    parts = ingredient.split()
    if not parts:
        return None, None, ingredient

    # Attempt to parse the first part as a quantity
    quantity = parse_quantity(parts[0])
    if quantity is not None:
        unit = parts[1] if len(parts) > 1 else None
        ingredient_name = ' '.join(parts[2:]) if len(parts) > 2 else None
    else:
        quantity = None
        unit = None
        ingredient_name = ingredient

    return quantity, unit, ingredient_name

def convert_to_grams(quantity, unit, ingredient_name):
    """
    Convert a given quantity and unit to grams using density information.
    """
    if quantity is None:
        return None

    # Standardize the ingredient name to match the density dictionary keys
    standardized_name = ingredient_name.lower().strip()

    # Check if the unit is recognized
    if unit and unit.lower() in UNIT_CONVERSIONS:
        conversion_factor = UNIT_CONVERSIONS[unit.lower()]
        if unit.lower() in ['g', 'gram', 'grams']:
            return quantity * conversion_factor
        elif unit.lower() in ['kg', 'kilogram', 'kilograms']:
            return quantity * conversion_factor
        elif unit.lower() in ['ml', 'milliliter', 'milliliters', 'l', 'liter', 'liters']:
            if standardized_name in DENSITY_DICT:
                density = DENSITY_DICT[standardized_name]
                return quantity * conversion_factor * density
            else:
                print(f"Density information not available for '{ingredient_name}'.")
                return None
        else:
            # For volume units, convert to milliliters first
            volume_ml = quantity * conversion_factor
            if standardized_name in DENSITY_DICT:
                density = DENSITY_DICT[standardized_name]
                return volume_ml * density
            else:
                print(f"Density information not available for '{ingredient_name}'.")
                return None
    else:
        print(f"Unrecognized unit '{unit}' for ingredient '{ingredient_name}'.")
        return None

def parse_ingredients(ingredients):
    """
    Process a list of ingredient strings into structured data.
    """
    parsed_data = []
    for item in ingredients:
        quantity, unit, ingredient_name = parse_ingredient(item)
        grams = convert_to_grams(quantity, unit, ingredient_name)
        parsed_data.append({
            'Quantity': quantity,
            'Unit': unit,
            'Ingredient': ingredient_name,
            'Grams': grams,
            'Original': item
        })
    return parsed_data

if __name__ == "__main__":
    args = get_args()
    recipe_url = args.url

    # Extract recipe details
    title, ingredients = extract_recipe(recipe_url)

    # Parse the ingredients
    parsed_ingredients = parse_ingredients(ingredients)

    # Create a DataFrame for parsed ingredients
    # ::contentReference[oaicite:0]{index=0}
    df = pd.DataFrame(parsed_ingredients)
 