"""Test script to verify ingredient format fix"""
import sys
sys.path.insert(0, '.')

from vision import extract_ingredients
import json

# Test with a cached image
print("Testing ingredient format fix...")
print("-" * 50)

result = extract_ingredients('samples/fridge_2.png')

print(f"\nResult type: {type(result)}")

if isinstance(result, dict):
    ingredients = result.get('ingredients', [])
    labeled_path = result.get('labeled_image_path')
    print(f"Labeled image path: {labeled_path}")
else:
    ingredients = result

print(f"\nIngredients type: {type(ingredients)}")
print(f"Number of ingredients: {len(ingredients)}")

if ingredients:
    print(f"\nFirst ingredient: {ingredients[0]}")
    print(f"First ingredient type: {type(ingredients[0])}")
    
    # Check if it's in correct format
    if isinstance(ingredients[0], dict):
        print("\n[SUCCESS] Ingredients are in dict format")
        print(f"   Has 'name' key: {'name' in ingredients[0]}")
        print(f"   Has 'count' key: {'count' in ingredients[0]}")
        
        # Show first 3 ingredients
        print("\nFirst 3 ingredients:")
        for i, ing in enumerate(ingredients[:3]):
            print(f"  {i+1}. {ing}")
    elif isinstance(ingredients[0], str):
        print("\n[FAIL] Ingredients are still strings")
    else:
        print(f"\n[UNEXPECTED] Ingredient type is {type(ingredients[0])}")

print("\n" + "-" * 50)
print("Test complete!")

# Made with Bob
