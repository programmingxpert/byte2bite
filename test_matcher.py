from recipe_matcher import find_best_recipes

# Test with the 11 ingredients from the user
ingredients = ['flour', 'butter', 'bread', 'sauce', 'cheese', 'juice', 'eggs', 'milk', 'pasta', 'soda', 'yogurt']

print(f"Testing with {len(ingredients)} ingredients: {', '.join(ingredients)}\n")

results = find_best_recipes(ingredients, top_n=20, dietary_preference='all')

print(f"Found {len(results)} matching recipes:\n")
print("=" * 80)

for i, recipe in enumerate(results[:15], 1):
    print(f"\n{i}. {recipe['name']}")
    print(f"   Match: {recipe['score']}% ({recipe['ingredients_used']} user ingredients used)")
    print(f"   Matched: {', '.join(recipe['matched'][:5])}{'...' if len(recipe['matched']) > 5 else ''}")
    print(f"   Missing: {', '.join(recipe['missing'][:3])}{'...' if len(recipe['missing']) > 3 else ''}")
    print(f"   Cuisine: {recipe['cuisine']} | Difficulty: {recipe['difficulty']} | Time: {recipe['time']}")

print("\n" + "=" * 80)
print(f"\nTotal recipes found: {len(results)}")

# Made with Bob
