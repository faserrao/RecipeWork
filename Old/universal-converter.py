import json
import pandas as pd

# Conversion factors for common cooking units
CONVERSION_FACTORS = {
    "teaspoon_to_tablespoon": 1 / 3,
    "tablespoon_to_cup": 1 / 16,
    "cup_to_ounce": 8,
    "ounce_to_gram": 28.3495,
    "gram_to_kilogram": 1 / 1000,
    "ounce_to_milliliter": 29.5735,
    "cup_to_milliliter": 240,
    "liter_to_milliliter": 1000,
    "pound_to_ounce": 16,
    "pound_to_gram": 453.592,
}

# Example ingredient densities (grams per cup, varies by ingredient)
INGREDIENT_DENSITIES = {
    "flour": 120,  # grams per cup
    "sugar": 200,
    "butter": 227,
    "milk": 240,
    "water": 240,
}

def convert_unit(value, from_unit, to_unit):
    """Converts between units based on predefined conversion factors."""
    key = f"{from_unit}_to_{to_unit}"
    if key in CONVERSION_FACTORS:
        return value * CONVERSION_FACTORS[key]
    else:
        return f"Conversion from {from_unit} to {to_unit} not available."

def calculate_cost_per_unit(total_cost, total_amount):
    """Calculates cost per unit based on total cost and amount."""
    if total_amount == 0:
        return "Cannot divide by zero."
    return total_cost / total_amount

def ingredient_amount_per_unit(ingredient, amount, from_unit, to_unit):
    """Converts ingredient amount between weight and volume using known densities."""
    if ingredient not in INGREDIENT_DENSITIES:
        return f"Density data not available for {ingredient}."
    
    # Convert volume (cups) to weight (grams) if needed
    if from_unit == "cup" and to_unit == "gram":
        return amount * INGREDIENT_DENSITIES[ingredient]
    elif from_unit == "gram" and to_unit == "cup":
        return amount / INGREDIENT_DENSITIES[ingredient]
    else:
        return convert_unit(amount, from_unit, to_unit)

def generate_conversion_table():
    """Generates a table for common conversions."""
    data = []
    for key, factor in CONVERSION_FACTORS.items():
        from_unit, to_unit = key.split("_to_")
        data.append({"From Unit": from_unit, "To Unit": to_unit, "Factor": factor})
    df = pd.DataFrame(data)
    return df

# Example usage
if __name__ == "__main__":
    print("Unit Conversion:", convert_unit(2, "cup", "ounce"))
    print("Cost per Unit:", calculate_cost_per_unit(5.00, 16))  # Cost per ounce
    print("Ingredient Amount:", ingredient_amount_per_unit("flour", 2, "cup", "gram"))
    print("\nConversion Table:")
    print(generate_conversion_table())

