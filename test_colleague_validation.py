"""
Test script to verify colleague name uniqueness validation
Run this from the Django shell: python manage.py shell < test_colleague_validation.py
"""

from api.models import Colleague
from api.serializers import ColleagueSerializer
from rest_framework.test import APIRequestFactory

# Create a request factory
factory = APIRequestFactory()
request = factory.get('/')

print("=" * 70)
print("Testing Colleague Name Uniqueness Validation")
print("=" * 70)

# Test 1: Create a test colleague
print("\n✓ Test 1: Creating a test colleague named 'أحمد محمد'...")
colleague_data = {
    'name': 'أحمد محمد',
    'position': 'مهندس',
    'status': 'active'
}

serializer = ColleagueSerializer(data=colleague_data, context={'request': request})
if serializer.is_valid():
    test_colleague = serializer.save()
    print(f"  SUCCESS: Created colleague with ID {test_colleague.id}")
else:
    print(f"  FAILED: {serializer.errors}")

# Test 2: Try to create another with same name (exact match)
print("\n✓ Test 2: Attempting to create duplicate with exact name 'أحمد محمد'...")
duplicate_data = {
    'name': 'أحمد محمد',
    'position': 'دكتور',
    'status': 'promoted'
}

serializer2 = ColleagueSerializer(data=duplicate_data, context={'request': request})
if serializer2.is_valid():
    print("  FAILED: Should have been rejected as duplicate!")
    serializer2.save().delete()  # Clean up if accidentally created
else:
    print(f"  SUCCESS: Duplicate rejected! Error: {serializer2.errors['name'][0]}")

# Test 3: Try with different case
print("\n✓ Test 3: Attempting to create duplicate with different case 'احمد محمد'...")
case_duplicate_data = {
    'name': 'احمد محمد',  # Different case
    'position': 'مدرس',
    'status': 'active'
}

serializer3 = ColleagueSerializer(data=case_duplicate_data, context={'request': request})
if serializer3.is_valid():
    print("  FAILED: Should have been rejected (case-insensitive check)!")
    serializer3.save().delete()  # Clean up
else:
    print(f"  SUCCESS: Case-insensitive duplicate rejected! Error: {serializer3.errors['name'][0]}")

# Test 4: Try with extra whitespace
print("\n✓ Test 4: Attempting to create duplicate with whitespace '  أحمد محمد  '...")
whitespace_duplicate_data = {
    'name': '  أحمد محمد  ',  # Extra whitespace
    'position': 'مهندس',
    'status': 'active'
}

serializer4 = ColleagueSerializer(data=whitespace_duplicate_data, context={'request': request})
if serializer4.is_valid():
    print("  FAILED: Should have been rejected (whitespace trimmed)!")
    serializer4.save().delete()  # Clean up
else:
    print(f"  SUCCESS: Whitespace-trimmed duplicate rejected! Error: {serializer4.errors['name'][0]}")

# Test 5: Create a different colleague (should succeed)
print("\n✓ Test 5: Creating a different colleague 'سعيد علي'...")
different_data = {
    'name': 'سعيد علي',
    'position': 'طبيب',
    'status': 'active'
}

serializer5 = ColleagueSerializer(data=different_data, context={'request': request})
if serializer5.is_valid():
    test_colleague2 = serializer5.save()
    print(f"  SUCCESS: Created different colleague with ID {test_colleague2.id}")
else:
    print(f"  FAILED: {serializer5.errors}")

# Test 6: Update existing colleague without changing name (should succeed)
print(f"\n✓ Test 6: Updating colleague {test_colleague.id} position without changing name...")
update_data = {
    'name': 'أحمد محمد',  # Same name
    'position': 'مهندس أول',  # Changed position
    'status': 'promoted'
}

serializer6 = ColleagueSerializer(test_colleague, data=update_data, context={'request': request}, partial=True)
if serializer6.is_valid():
    serializer6.save()
    print("  SUCCESS: Updated colleague without name change")
else:
    print(f"  FAILED: {serializer6.errors}")

# Test 7: Update existing colleague to duplicate another's name (should fail)
print(f"\n✓ Test 7: Attempting to update colleague {test_colleague2.id} to duplicate name 'أحمد محمد'...")
bad_update_data = {
    'name': 'أحمد محمد',  # Trying to use existing name
}

serializer7 = ColleagueSerializer(test_colleague2, data=bad_update_data, context={'request': request}, partial=True)
if serializer7.is_valid():
    print("  FAILED: Should have been rejected as duplicate!")
else:
    print(f"  SUCCESS: Update to duplicate name rejected! Error: {serializer7.errors['name'][0]}")

# Cleanup
print("\n" + "=" * 70)
print("Cleaning up test data...")
if test_colleague:
    test_colleague.delete()
    print(f"  Deleted test colleague 'أحمد محمد'")
if test_colleague2:
    test_colleague2.delete()
    print(f"  Deleted test colleague 'سعيد علي'")

print("\n✓ All tests completed!")
print("=" * 70)
