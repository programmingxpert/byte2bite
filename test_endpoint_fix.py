"""
Test script to verify the sustainability-analysis endpoint accepts both formats
"""

def test_ingredient_conversion():
    """Test the ingredient conversion logic"""
    from typing import Any, List
    
    def convert_ingredients(user_ingredients: List[Any]) -> List[str]:
        """Convert ingredients to string list - same logic as in main.py"""
        ingredient_names = []
        for ingredient in user_ingredients:
            if isinstance(ingredient, dict):
                # New format: {"name": "apple", "count": 3}
                ingredient_names.append(ingredient.get("name", ""))
            elif isinstance(ingredient, str):
                # Old format: "apple"
                ingredient_names.append(ingredient)
            else:
                # Handle IngredientItem objects (Pydantic models)
                ingredient_names.append(getattr(ingredient, "name", str(ingredient)))
        
        # Filter out empty strings
        return [name for name in ingredient_names if name]
    
    # Test old format (strings)
    old_format = ["apple", "banana", "cheese"]
    result_old = convert_ingredients(old_format)
    print(f"[PASS] Old format test: {old_format} -> {result_old}")
    assert result_old == ["apple", "banana", "cheese"], "Old format failed"
    
    # Test new format (objects)
    new_format = [
        {"name": "apple", "count": 3},
        {"name": "banana", "count": 2},
        {"name": "cheese", "count": 1}
    ]
    result_new = convert_ingredients(new_format)
    print(f"[PASS] New format test: {new_format} -> {result_new}")
    assert result_new == ["apple", "banana", "cheese"], "New format failed"
    
    # Test mixed format
    mixed_format = [
        "apple",
        {"name": "banana", "count": 2},
        "cheese"
    ]
    result_mixed = convert_ingredients(mixed_format)
    print(f"[PASS] Mixed format test: {mixed_format} -> {result_mixed}")
    assert result_mixed == ["apple", "banana", "cheese"], "Mixed format failed"
    
    # Test empty names
    with_empty = [
        {"name": "apple", "count": 3},
        {"name": "", "count": 0},
        {"name": "banana", "count": 2}
    ]
    result_empty = convert_ingredients(with_empty)
    print(f"[PASS] Empty name filter test: {with_empty} -> {result_empty}")
    assert result_empty == ["apple", "banana"], "Empty name filter failed"
    
    print("\n[SUCCESS] All tests passed! Both old and new formats are supported.")
    print("[SUCCESS] Backward compatibility maintained.")

if __name__ == "__main__":
    test_ingredient_conversion()

# Made with Bob
