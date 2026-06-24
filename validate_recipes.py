import json

# Load recipes
with open('recipes.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# User's common ingredients
user_ingredients = [
    'milk', 'bread', 'yogurt', 'tomato', 'apple', 'watermelon', 
    'cucumber', 'orange', 'banana', 'lettuce', 'tomato sauce', 
    'peanut butter', 'cheese', 'pear', 'strawberry', 'butter', 
    'jelly', 'peanut'
]

# Get last 15 recipes (newly added)
new_recipes = data[-15:]

print(f"New recipes added: {len(new_recipes)}\n")
print("=" * 70)

total_matching = 0
for r in new_recipes:
    matching = [i for i in r['ingredients'] if i in user_ingredients]
    match_pct = (len(matching) / len(r['ingredients'])) * 100
    total_matching += len(matching)
    print(f"{r['name']}")
    print(f"  Total ingredients: {len(r['ingredients'])}")
    print(f"  Matching user list: {len(matching)} ({match_pct:.0f}%)")
    print(f"  Ingredients: {', '.join(r['ingredients'])}")
    print()

print("=" * 70)
print(f"\nSummary:")
print(f"  Total new recipes: {len(new_recipes)}")
print(f"  Average ingredients per recipe: {sum(len(r['ingredients']) for r in new_recipes) / len(new_recipes):.1f}")
print(f"  Total ingredient slots used: {sum(len(r['ingredients']) for r in new_recipes)}")
print(f"  Matching user ingredients: {total_matching}")
print(f"  Match rate: {(total_matching / sum(len(r['ingredients']) for r in new_recipes)) * 100:.1f}%")

# Made with Bob
