import requests
import json5
import re
from bs4 import BeautifulSoup

def extract_recipe(url):
    """Extracts recipe from a webpage using JSON-LD and HTML parsing."""
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Failed to fetch the page")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Try to find structured JSON-LD recipe data
    json_ld_scripts = soup.find_all("script", {"type": "application/ld+json"})
    
    for script in json_ld_scripts:
        try:
            data = json5.loads(script.string)
            if isinstance(data, list):  # Sometimes JSON-LD contains multiple objects
                for item in data:
                    if item.get("@type") == "Recipe":
                        return item
            elif data.get("@type") == "Recipe":
                return data
        except json5.JSONDecodeError:
            continue

    # Fallback: Extract from HTML elements if JSON-LD is missing
    recipe = {}
    title = soup.find("h1") or soup.find("title")
    recipe["name"] = title.get_text(strip=True) if title else "Unknown Recipe"

    ingredient_elements = soup.find_all(["li", "span"], class_=lambda x: x and "ingredient" in x.lower())
    print("\n📝 ingredient_elements:")
    print(ingredient_elements)

    # List to store parsed ingredients
    ingredient_list = []

    # Loop through each ingredient element
    for ingredient in ingredient_elements:
        quantity = ingredient.find("span", {"data-ingredient-quantity": "true"})
        unit = ingredient.find("span", {"data-ingredient-unit": "true"})
        name = ingredient.find("span", {"data-ingredient-name": "true"})

        # Extract text, handling missing values
        quantity_text = quantity.get_text(strip=True) if quantity else ""
        unit_text = unit.get_text(strip=True) if unit and unit.text.strip() else ""  # Avoid empty units
        name_text = name.get_text(strip=True) if name else ""

        # Store ingredient data
        ingredient_data = {
            "quantity": quantity_text,
            "unit": unit_text,
            "name": name_text
        }
        
        ingredient_list.append(ingredient_data)

    print("\n📝 ingredient_list:")
    print(ingredient_list)

    recipe["ingredient_list"] = ingredient_list
    
    # Convert ingredient_list elements to plain text before parsing
    # recipe["ingredient_list"] = [i.get_text(strip=True) for i in ingredient_list if i.get_text(strip=True)]

    print("\n📝 recipe[ingredient_list]:")
    print(recipe["ingredient_list"])

    recipe["parsed_ingredients"] = [parse_ingredient(i) for i in recipe["ingredient_list"]]

    print("\n📝 Parsed Ingredients:")
    print(recipe["parsed_ingredients"])

    instructions = soup.find_all(["li", "p"], class_=lambda x: x and "instruction" in x.lower())
    recipe["instructions"] = [step.get_text(strip=True) for step in instructions if step.get_text(strip=True)]

    return recipe

def parse_ingredient(ingredient_text):
    """Parses an ingredient string into amount, unit, and ingredient."""
    pattern = re.compile(r"^(\S+)\s+(\S+)\s+(.+)$")  # Matches amount, unit, and ingredient
    
    if not ingredient_text:  # Ensure ingredient_text is valid
        return {"amount": None, "unit": None, "ingredient": None}

    match = pattern.match(ingredient_text.strip())
    if match:
        amount, unit, ingredient = match.groups()
        return {"amount": amount, "unit": unit, "ingredient": ingredient}
    else:
        # If no match, assume missing amount or unit
        return {"amount": None, "unit": None, "ingredient": ingredient_text.strip()}

def display_recipe(recipe):
    """Displays extracted recipe information."""
    if not recipe:
        print("No recipe found.")
        return

    print("\n=== Recipe: {} ===".format(recipe.get("name", "Unknown")))
    if "image" in recipe:
        print("📸 Image: {}".format(recipe["image"]))
    
    print("\n📝 Description:")
    print(recipe.get("description", "No description available."))

    print("\n⏳ Time:")
    print("Prep Time:", recipe.get("prepTime", "N/A"))
    print("Cook Time:", recipe.get("cookTime", "N/A"))
    print("Total Time:", recipe.get("totalTime", "N/A"))

    print("\n🍽️ Ingredients:")
    for ing in recipe.get("parsed_ingredients", []):
        print(f" - {ing['amount'] or ''} {ing['unit'] or ''} {ing['ingredient']}")

    print("\n👨‍🍳 Instructions:")
    for idx, step in enumerate(recipe.get("recipeInstructions", recipe.get("instructions", [])), 1):
        if isinstance(step, dict) and "text" in step:
            print(f" {idx}. {step['text']}")
        else:
            print(f" {idx}. {step}")

# Example usage
url = input("Enter recipe URL: ")
recipe_data = extract_recipe(url)
display_recipe(recipe_data)
