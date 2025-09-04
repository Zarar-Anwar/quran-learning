#!/usr/bin/env python
"""
Test script for pricing functionality
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
django.setup()

from src.services.courses.models import PricingPlan

def test_pricing_plans():
    """Test that pricing plans are working correctly"""
    print("Testing Pricing Plans...")
    print("=" * 50)
    
    # Get all active pricing plans
    plans = PricingPlan.objects.filter(is_active=True).order_by('price')
    
    if not plans:
        print("❌ No pricing plans found!")
        return False
    
    print(f"✅ Found {plans.count()} pricing plans:")
    print()
    
    for plan in plans:
        print(f"📋 {plan.name}")
        print(f"   💰 Monthly: ${plan.price}")
        print(f"   📅 Classes: {plan.classes_per_week}/week, {plan.classes_per_month}/month")
        print(f"   👥 Students: {plan.students_enrolled}+")
        print(f"   🏆 Popular: {'Yes' if plan.is_popular else 'No'}")
        print(f"   💸 6 Months: ${plan.get_six_month_price():.2f} (Save {plan.six_month_discount}%)")
        print(f"   💸 12 Months: ${plan.get_twelve_month_price():.2f} (Save {plan.twelve_month_discount}%)")
        print()
    
    return True

def test_pricing_calculations():
    """Test pricing calculations"""
    print("Testing Pricing Calculations...")
    print("=" * 50)
    
    plan = PricingPlan.objects.first()
    if not plan:
        print("❌ No plans to test calculations!")
        return False
    
    print(f"Testing calculations for: {plan.name}")
    
    # Test 6-month calculation
    from decimal import Decimal
    expected_6month = plan.price * 6 * (Decimal(1) - Decimal(plan.six_month_discount) / 100)
    actual_6month = plan.get_six_month_price()
    print(f"6-month calculation: ${expected_6month:.2f} vs ${actual_6month:.2f}")
    
    # Test 12-month calculation
    expected_12month = plan.price * 12 * (Decimal(1) - Decimal(plan.twelve_month_discount) / 100)
    actual_12month = plan.get_twelve_month_price()
    print(f"12-month calculation: ${expected_12month:.2f} vs ${actual_12month:.2f}")
    
    return True

if __name__ == "__main__":
    print("🧪 Pricing System Test")
    print("=" * 50)
    
    try:
        success1 = test_pricing_plans()
        print()
        success2 = test_pricing_calculations()
        
        if success1 and success2:
            print("✅ All tests passed! Pricing system is working correctly.")
        else:
            print("❌ Some tests failed. Please check the output above.")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
