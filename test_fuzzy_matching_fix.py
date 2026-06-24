"""
Test script to verify the fuzzy matching bug fix
Tests that ingredients like "water" don't match "watermelon"
and "apple" doesn't match "pineapple"
"""

from recipe_matcher import find_best_recipes

def test_false_positive_prevention():
    """Test that the fix prevents false positive matches"""
    
    print("=" * 80)
    print("TESTING FUZZY MATCHING BUG FIX")
    print("=" * 80)
    
    # Test Case 1: User has apple, water, cherry (the reported bug case)
    print("\nTest Case 1: User has apple (x2), water (x3), cherry (x1)")
    print("-" * 80)
    
    user_ingredients = [
        {"name": "apple", "count": 2},
        {"name": "water", "count": 3},
        {"name": "cherry", "count": 1}
    ]
    
    recipes = find_best_recipes(user_ingredients, top_n=5)
    
    print(f"\n[OK] Found {len(recipes)} matching recipes\n")
    
    # Check for false positives
    false_positives_found = False
    
    for i, recipe in enumerate(recipes[:3], 1):
        print(f"{i}. {recipe['name']} - {recipe['score']}% match")
        print(f"   Matched ingredients: {recipe['matched']}")
        
        # Check for false positives
        for matched_ing in recipe['matched']:
            matched_lower = matched_ing.lower()
            
            # Check if watermelon is incorrectly matched (should NOT be)
            if 'watermelon' in matched_lower and 'water' in [ing['name'] for ing in user_ingredients]:
                print(f"   [X] FALSE POSITIVE: '{matched_ing}' matched when user only has 'water'")
                false_positives_found = True
            
            # Check if pineapple is incorrectly matched (should NOT be)
            if 'pineapple' in matched_lower and 'apple' in [ing['name'] for ing in user_ingredients]:
                print(f"   [X] FALSE POSITIVE: '{matched_ing}' matched when user only has 'apple'")
                false_positives_found = True
        
        print()
    
    # Test Case 2: Verify legitimate matches still work
    print("\nTest Case 2: Verify legitimate fuzzy matches still work")
    print("-" * 80)
    
    user_ingredients_2 = [
        {"name": "cheese", "count": 1},
        {"name": "tomato", "count": 2}
    ]
    
    recipes_2 = find_best_recipes(user_ingredients_2, top_n=3)
    
    print(f"\n[OK] Found {len(recipes_2)} matching recipes\n")
    
    legitimate_matches_work = False
    
    for i, recipe in enumerate(recipes_2[:3], 1):
        print(f"{i}. {recipe['name']} - {recipe['score']}% match")
        print(f"   Matched ingredients: {recipe['matched']}")
        
        # Check if "cheddar cheese" or similar matches "cheese" (should work)
        for matched_ing in recipe['matched']:
            if 'cheese' in matched_ing.lower():
                legitimate_matches_work = True
                print(f"   [OK] LEGITIMATE MATCH: '{matched_ing}' correctly matched with 'cheese'")
        
        print()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    if not false_positives_found:
        print("[PASS] No false positive matches detected!")
        print("   - 'water' does NOT match 'watermelon'")
        print("   - 'apple' does NOT match 'pineapple'")
    else:
        print("[FAIL] False positive matches still detected!")
    
    if legitimate_matches_work:
        print("[PASS] Legitimate fuzzy matches still work!")
        print("   - 'cheese' correctly matches 'cheddar cheese', etc.")
    else:
        print("[WARNING] No legitimate fuzzy matches found in test")
    
    print("\n" + "=" * 80)
    
    return not false_positives_found and legitimate_matches_work


if __name__ == "__main__":
    success = test_false_positive_prevention()
    
    if success:
        print("\n[SUCCESS] ALL TESTS PASSED! The bug is fixed!")
    else:
        print("\n[WARNING] Some tests failed. Review the output above.")
    
    exit(0 if success else 1)

# Made with Bob
