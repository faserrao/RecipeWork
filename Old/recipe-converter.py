def convert_measurement(amount, from_unit, to_unit):
    conversion_factors = {
        "teaspoon": {
            "tablespoon": 1/3, "cup": 1/48, "milliliter": 4.92892, "fluid ounce": 1/6,
            "gram": 5, "ounce": 1/6
        },
        "tablespoon": {
            "teaspoon": 3, "cup": 1/16, "milliliter": 14.7868, "fluid ounce": 1/2,
            "gram": 15, "ounce": 1/2
        },
        "cup": {
            "teaspoon": 48, "tablespoon": 16, "milliliter": 236.588, "fluid ounce": 8,
            "gram": 240, "ounce": 8
        },
        "milliliter": {
            "teaspoon": 1/4.92892, "tablespoon": 1/14.7868, "cup": 1/236.588,
            "fluid ounce": 1/29.5735, "gram": 1, "ounce": 1/28.35
        },
        "fluid ounce": {
            "teaspoon": 6, "tablespoon": 2, "cup": 1/8, "milliliter": 29.5735,
            "gram": 30, "ounce": 1
        },
        "gram": {
            "teaspoon": 1/5, "tablespoon": 1/15, "cup": 1/240, "milliliter": 1,
            "fluid ounce": 1/30, "ounce": 1/28.35
        },
        "ounce": {
            "teaspoon": 6, "tablespoon": 2, "cup": 1/8, "milliliter": 28.35,
            "fluid ounce": 1, "gram": 28.35
        }
    }
    
    if from_unit not in conversion_factors or to_unit not in conversion_factors[from_unit]:
        return "Conversion not available"
    
    return amount * conversion_factors[from_unit][to_unit]

# Example Usage
amount = 2
from_unit = "cup"
to_unit = "milliliter"
result = convert_measurement(amount, from_unit, to_unit)
print(f"{amount} {from_unit} = {result:.2f} {to_unit}")

