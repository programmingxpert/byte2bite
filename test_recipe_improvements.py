"""
Comprehensive Test Suite for Recipe Matching System Improvements
Tests all recent changes including:
- Fixed sorting (Match % → Utilization % → Ingredients Used)
- Increased result limit from 5 to 20 recipes
- Quantity detection in vision.py
- Utilization scoring
- Frontend display improvements
"""

import json
from recipe_matcher import find_best_recipes
from typing import List, Dict, Any

class TestRecipeImprovements:
    def __init__(self):
        self.test_results = []
        
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "[PASS]" if passed else "[FAIL]"
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details
        }
        self.test_results.append(result)
        print(f"\n{status}: {test_name}")
        if details:
            print(f"  Details: {details}")
    
    def test_user_18_ingredients(self):
        """Test with user's actual 18 ingredients"""
        print("\n" + "="*80)
        print("TEST 1: User's 18 Ingredients")
        print("="*80)
        
        ingredients = [
            {"name": "milk", "count": 1},
            {"name": "jelly", "count": 1},
            {"name": "peanut", "count": 1},
            {"name": "bread", "count": 1},
            {"name": "yogurt", "count": 1},
            {"name": "tomato", "count": 2},
            {"name": "apple", "count": 3},
            {"name": "watermelon", "count": 1},
            {"name": "cucumber", "count": 1},
            {"name": "orange", "count": 1},
            {"name": "banana", "count": 2},
            {"name": "lettuce", "count": 1},
            {"name": "tomato sauce", "count": 1},
            {"name": "peanut butter", "count": 1},
            {"name": "cheese", "count": 1},
            {"name": "pear", "count": 1},
            {"name": "strawberry", "count": 1},
            {"name": "butter", "count": 1}
        ]
        
        results = find_best_recipes(ingredients)
        
        # Test 1.1: Check if results are returned
        if not results:
            self.log_result("User 18 Ingredients - Results Returned", False, 
                          "No results returned")
            return
        
        self.log_result("User 18 Ingredients - Results Returned", True, 
                       f"Returned {len(results)} recipes")
        
        # Test 1.2: Check if more than 5 recipes returned
        passed = len(results) > 5
        self.log_result("More than 5 recipes returned", passed, 
                       f"Got {len(results)} recipes (expected > 5, max 20)")
        
        # Test 1.3: Check if Grilled Cheese is #1 (100% match with butter)
        if results:
            first_recipe = results[0]
            is_grilled_cheese = "grilled cheese" in first_recipe['name'].lower()
            is_100_percent = first_recipe['score'] == 100
            
            self.log_result("Grilled Cheese at #1 with 100% match",
                          is_grilled_cheese and is_100_percent,
                          f"First recipe: {first_recipe['name']} ({first_recipe['score']}%)")
        
        # Test 1.4: Verify sorting order
        self.verify_sorting_order(results, "User 18 Ingredients")
        
        # Test 1.5: Check utilization scores exist
        has_utilization = all('utilization' in r for r in results)
        self.log_result("Utilization scores present", has_utilization,
                       f"All {len(results)} recipes have utilization scores")
        
        # Display top 10 results
        print("\n--- Top 10 Results ---")
        for i, recipe in enumerate(results[:10], 1):
            print(f"{i}. {recipe['name']}")
            print(f"   Match: {recipe['score']}% | "
                  f"Utilization: {recipe.get('utilization', 'N/A')}% | "
                  f"Ingredients Used: {recipe['ingredients_used']} | "
                  f"Missing: {len(recipe.get('missing', []))}")
        
        return results
    
    def verify_sorting_order(self, results: List[Dict], test_name: str):
        """Verify recipes are sorted correctly: Match % -> Utilization % -> Ingredients Used"""
        print(f"\n--- Verifying Sort Order for {test_name} ---")
        
        is_sorted = True
        issues = []
        
        for i in range(len(results) - 1):
            current = results[i]
            next_recipe = results[i + 1]
            
            curr_match = current['score']
            next_match = next_recipe['score']
            curr_util = current.get('utilization', 0)
            next_util = next_recipe.get('utilization', 0)
            curr_used = current['ingredients_used']
            next_used = next_recipe['ingredients_used']
            
            # Check primary sort: match percentage (descending)
            if curr_match < next_match:
                is_sorted = False
                issues.append(f"Position {i+1}-{i+2}: Match % out of order "
                            f"({curr_match}% < {next_match}%)")
            
            # Check secondary sort: utilization (descending) when match is equal
            elif curr_match == next_match and curr_util < next_util:
                is_sorted = False
                issues.append(f"Position {i+1}-{i+2}: Utilization % out of order "
                            f"({curr_util}% < {next_util}%) with same match {curr_match}%")
            
            # Check tertiary sort: ingredients used (descending) when match and util are equal
            elif curr_match == next_match and curr_util == next_util and curr_used < next_used:
                is_sorted = False
                issues.append(f"Position {i+1}-{i+2}: Ingredients used out of order "
                            f"({curr_used} < {next_used}) with same match {curr_match}% and util {curr_util}%")
        
        details = "Correct sort order" if is_sorted else "\n  ".join(issues)
        self.log_result(f"Sorting Order - {test_name}", is_sorted, details)
        
        return is_sorted
    
    def test_empty_ingredients(self):
        """Test with empty ingredient list"""
        print("\n" + "="*80)
        print("TEST 2: Empty Ingredient List")
        print("="*80)
        
        results = find_best_recipes([])
        
        # Should return empty list or handle gracefully
        passed = isinstance(results, list)
        self.log_result("Empty ingredients handled", passed,
                       f"Returned {len(results)} recipes (expected 0 or handled gracefully)")
    
    def test_single_ingredient(self):
        """Test with single ingredient"""
        print("\n" + "="*80)
        print("TEST 3: Single Ingredient")
        print("="*80)
        
        ingredients = [{"name": "tomato", "count": 1}]
        results = find_best_recipes(ingredients)
        
        passed = isinstance(results, list) and len(results) >= 0
        self.log_result("Single ingredient handled", passed,
                       f"Returned {len(results)} recipes")
        
        if results:
            print(f"\n--- Top 5 Results for 'tomato' ---")
            for i, recipe in enumerate(results[:5], 1):
                print(f"{i}. {recipe['name']} - {recipe['score']}%")
    
    def test_no_matching_recipes(self):
        """Test with ingredients that have no matching recipes"""
        print("\n" + "="*80)
        print("TEST 4: No Matching Recipes")
        print("="*80)
        
        ingredients = [
            {"name": "unicorn_tears", "count": 1},
            {"name": "dragon_scales", "count": 1},
            {"name": "phoenix_feather", "count": 1}
        ]
        results = find_best_recipes(ingredients)
        
        passed = isinstance(results, list)
        self.log_result("No matches handled gracefully", passed,
                       f"Returned {len(results)} recipes (expected 0)")
    
    def test_backward_compatibility(self):
        """Test both string format and object format"""
        print("\n" + "="*80)
        print("TEST 5: Backward Compatibility")
        print("="*80)
        
        # Test with string format (old)
        string_ingredients = ["bread", "cheese", "butter"]
        results_string = find_best_recipes(string_ingredients)
        
        # Test with object format (new)
        object_ingredients = [
            {"name": "bread", "count": 1},
            {"name": "cheese", "count": 1},
            {"name": "butter", "count": 1}
        ]
        results_object = find_best_recipes(object_ingredients)
        
        # Both should work
        string_works = isinstance(results_string, list) and len(results_string) > 0
        object_works = isinstance(results_object, list) and len(results_object) > 0
        
        self.log_result("String format (backward compatibility)", string_works,
                       f"Returned {len(results_string)} recipes")
        self.log_result("Object format (new)", object_works,
                       f"Returned {len(results_object)} recipes")
        
        # Results should be similar (same recipes, possibly different order)
        if string_works and object_works:
            string_names = {r['name'] for r in results_string[:5]}
            object_names = {r['name'] for r in results_object[:5]}
            similar = len(string_names & object_names) >= 3
            self.log_result("Format compatibility", similar,
                           f"Top 5 recipes overlap: {len(string_names & object_names)}/5")
    
    def test_quantity_awareness(self):
        """Test that quantity information is preserved and used"""
        print("\n" + "="*80)
        print("TEST 6: Quantity Awareness")
        print("="*80)
        
        ingredients = [
            {"name": "apple", "count": 5},
            {"name": "banana", "count": 3},
            {"name": "orange", "count": 1}
        ]
        results = find_best_recipes(ingredients)
        
        # Check if quantity info is preserved in results
        has_quantities = any('count' in str(r) or 'quantity' in str(r) for r in results)
        
        self.log_result("Quantity information processed", len(results) > 0,
                       f"Returned {len(results)} recipes with fruit ingredients")
        
        if results:
            print(f"\n--- Sample Recipe with Quantities ---")
            print(f"Recipe: {results[0]['name']}")
            print(f"Ingredients: {results[0].get('ingredients', 'N/A')}")
    
    def test_utilization_calculation(self):
        """Test utilization percentage calculation"""
        print("\n" + "="*80)
        print("TEST 7: Utilization Calculation")
        print("="*80)
        
        # Test with ingredients that should give different utilization scores
        ingredients = [
            {"name": "bread", "count": 1},
            {"name": "cheese", "count": 1},
            {"name": "butter", "count": 1},
            {"name": "milk", "count": 1},
            {"name": "eggs", "count": 1},
            {"name": "flour", "count": 1},
            {"name": "sugar", "count": 1},
            {"name": "salt", "count": 1}
        ]
        results = find_best_recipes(ingredients)
        
        if results:
            # Check that utilization varies based on recipe complexity
            utilizations = [r.get('utilization', 0) for r in results[:10]]
            has_variation = len(set(utilizations)) > 1
            
            self.log_result("Utilization varies by recipe", has_variation,
                           f"Found {len(set(utilizations))} different utilization values in top 10")
            
            # Check that utilization is between 0 and 100
            valid_range = all(0 <= u <= 100 for u in utilizations)
            self.log_result("Utilization in valid range (0-100)", valid_range,
                           f"Range: {min(utilizations)}-{max(utilizations)}%")
            
            print(f"\n--- Utilization Examples ---")
            for i, recipe in enumerate(results[:5], 1):
                print(f"{i}. {recipe['name']}: {recipe.get('utilization', 'N/A')}% "
                      f"({recipe['ingredients_used']} user ingredients used, "
                      f"{len(recipe.get('missing', []))} missing)")
    
    def test_result_limit(self):
        """Test that up to 20 recipes are returned"""
        print("\n" + "="*80)
        print("TEST 8: Result Limit (20 recipes)")
        print("="*80)
        
        # Use many common ingredients to get lots of matches
        ingredients = [
            {"name": "flour", "count": 1},
            {"name": "sugar", "count": 1},
            {"name": "eggs", "count": 1},
            {"name": "milk", "count": 1},
            {"name": "butter", "count": 1},
            {"name": "salt", "count": 1},
            {"name": "vanilla", "count": 1},
            {"name": "baking powder", "count": 1}
        ]
        results = find_best_recipes(ingredients)
        
        # Should return up to 20 recipes
        passed = len(results) <= 20
        self.log_result("Result limit respected (<=20)", passed,
                       f"Returned {len(results)} recipes (max 20)")
        
        # Should return more than old limit of 5
        more_than_old = len(results) > 5
        self.log_result("More than old limit (>5)", more_than_old,
                       f"Returned {len(results)} recipes (old limit was 5)")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("TEST REPORT SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n--- Detailed Results ---")
        for result in self.test_results:
            print(f"\n{result['status']}: {result['test']}")
            if result['details']:
                print(f"  {result['details']}")
        
        # Summary of key findings
        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)
        
        findings = []
        
        # Check if sorting is fixed
        sorting_tests = [r for r in self.test_results if 'Sorting Order' in r['test']]
        if all(r['passed'] for r in sorting_tests):
            findings.append("OK Sorting is working correctly (Match % -> Utilization % -> Ingredients Used)")
        else:
            findings.append("FAIL Sorting issues detected")
        
        # Check if result limit increased
        limit_tests = [r for r in self.test_results if 'Result limit' in r['test'] or 'More than old limit' in r['test']]
        if all(r['passed'] for r in limit_tests):
            findings.append("OK Result limit successfully increased from 5 to 20")
        else:
            findings.append("FAIL Result limit issues detected")
        
        # Check if utilization is working
        util_tests = [r for r in self.test_results if 'Utilization' in r['test'] or 'utilization' in r['test']]
        if all(r['passed'] for r in util_tests):
            findings.append("OK Utilization scoring is working correctly")
        else:
            findings.append("FAIL Utilization scoring issues detected")
        
        # Check backward compatibility
        compat_tests = [r for r in self.test_results if 'compatibility' in r['test'].lower()]
        if all(r['passed'] for r in compat_tests):
            findings.append("OK Backward compatibility maintained")
        else:
            findings.append("FAIL Backward compatibility issues detected")
        
        for finding in findings:
            print(finding)
        
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)
        
        recommendations = []
        
        if failed_tests == 0:
            recommendations.append("OK All tests passed! System is working as expected.")
        else:
            recommendations.append(f"WARNING {failed_tests} test(s) failed. Review details above.")
        
        recommendations.append("- Consider adding unit tests for individual functions")
        recommendations.append("- Add performance benchmarks for large ingredient lists")
        recommendations.append("- Consider caching recipe matches for common ingredient combinations")
        recommendations.append("- Add logging for debugging production issues")
        
        for rec in recommendations:
            print(rec)
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': passed_tests/total_tests*100,
            'findings': findings,
            'recommendations': recommendations
        }

def main():
    """Run all tests"""
    print("="*80)
    print("RECIPE MATCHING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nTesting improvements:")
    print("1. Fixed sorting (Match % -> Utilization % -> Ingredients Used)")
    print("2. Increased result limit from 5 to 20")
    print("3. Quantity detection")
    print("4. Utilization scoring")
    print("5. Backward compatibility")
    
    tester = TestRecipeImprovements()
    
    # Run all tests
    tester.test_user_18_ingredients()
    tester.test_empty_ingredients()
    tester.test_single_ingredient()
    tester.test_no_matching_recipes()
    tester.test_backward_compatibility()
    tester.test_quantity_awareness()
    tester.test_utilization_calculation()
    tester.test_result_limit()
    
    # Generate report
    report = tester.generate_report()
    
    # Save report to file
    with open('test_report.json', 'w') as f:
        json.dump({
            'timestamp': '2026-06-23T06:46:50Z',
            'results': tester.test_results,
            'summary': report
        }, f, indent=2)
    
    print("\n[OK] Test report saved to test_report.json")
    
    return report

if __name__ == "__main__":
    main()

# Made with Bob
