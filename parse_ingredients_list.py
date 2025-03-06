import re

def parse_ingredient(ingredient_text):
    """Parses an ingredient string into amount, unit, and ingredient."""
    pattern = re.compile(r"^(\S+)\s+(\S+)\s+(.+)$")  # Matches amount, unit, and ingredient
    
    match = pattern.match(ingredient_text.strip())
    if match:
        amount, unit, ingredient = match.groups()
        return {"amount": amount, "unit": unit, "ingredient": ingredient}
    else:
        # If no match, assume missing amount or unit
        return {"amount": None, "unit": None, "ingredient": ingredient_text.strip()}

# Example usage
ingredient_list = [
    "2 cups flour",
    "1 cup sugar",
    "½ teaspoon salt",
    "1 tbsp vanilla extract",
    "3 large eggs"
]

parsed_ingredients = [parse_ingredient(ing) for ing in ingredient_list]

# Print results
for ing in parsed_ingredients:
    print(ing)
