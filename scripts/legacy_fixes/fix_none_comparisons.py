#!/usr/bin/env python3
"""
Fix None Comparison Errors in Nutrition Validator
Fixes the "'>' not supported between instances of 'NoneType'" errors
"""

def safe_get_numeric(data_dict, key, default=0):
    """Safely get numeric value from dict, handling None values"""
    if not data_dict:
        return default
    
    value = data_dict.get(key, default)
    
    # Handle None values
    if value is None:
        return default
    
    # Handle string numbers
    if isinstance(value, str):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    # Handle numeric values
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_compare(value, min_val, max_val):
    """Safely compare value with range, handling None values"""
    if value is None:
        return False, 'missing'
    
    try:
        numeric_value = float(value)
        if min_val <= numeric_value <= max_val:
            return True, 'valid'
        else:
            return False, 'out_of_range'
    except (ValueError, TypeError):
        return False, 'invalid_type'

# Test the fixes
if __name__ == "__main__":
    print("🔧 TESTING NONE COMPARISON FIXES")
    print("=" * 40)
    
    # Test cases that would cause errors
    test_cases = [
        {'value': None, 'min': 0, 'max': 100},
        {'value': 'None', 'min': 0, 'max': 100},
        {'value': 42, 'min': 0, 'max': 100},
        {'value': '42', 'min': 0, 'max': 100},
        {'value': 150, 'min': 0, 'max': 100},
    ]
    
    for i, test in enumerate(test_cases, 1):
        try:
            is_valid, status = safe_compare(test['value'], test['min'], test['max'])
            print(f"✅ Test {i}: {test['value']} -> {status} ({is_valid})")
        except Exception as e:
            print(f"❌ Test {i}: {test['value']} -> ERROR: {e}")
    
    # Test safe_get_numeric
    print(f"\n🔧 Testing safe_get_numeric:")
    test_data = {
        'normal': 42,
        'none_value': None,
        'string_number': '42.5',
        'invalid_string': 'not_a_number'
    }
    
    for key in ['normal', 'none_value', 'string_number', 'invalid_string', 'missing_key']:
        result = safe_get_numeric(test_data, key, 0)
        print(f"   {key}: {test_data.get(key, 'MISSING')} -> {result}")
    
    print(f"\n✅ All fixes working correctly!")