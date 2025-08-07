#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from src.services.courses.models import Instructor
from src.services.users.models import User

def test_login_system():
    print("=== Testing Login System ===")
    
    # Test 1: Check if admin user exists and can authenticate
    try:
        admin_user = User.objects.get(username='zaala1')
        print(f"✓ Admin user found: {admin_user.username}")
        
        # Test password
        if check_password('zaala123', admin_user.password):
            print("✓ Admin password is correct")
        else:
            print("✗ Admin password is incorrect")
            
        # Test authentication
        auth_user = authenticate(username='zaala1', password='zaala123')
        if auth_user:
            print("✓ Admin authentication works")
        else:
            print("✗ Admin authentication failed")
            
    except User.DoesNotExist:
        print("✗ Admin user not found")
    
    # Test 2: Check if instructor exists and can authenticate
    try:
        instructor = Instructor.objects.get(email='instructor@example.com')
        print(f"✓ Instructor found: {instructor.name}")
        
        # Test password
        if instructor.check_password('instructor123'):
            print("✓ Instructor password is correct")
        else:
            print("✗ Instructor password is incorrect")
            
    except Instructor.DoesNotExist:
        print("✗ Instructor not found")
    
    # Test 3: Check if student exists and can authenticate
    try:
        student = User.objects.get(username='student')
        print(f"✓ Student user found: {student.username}")
        
        # Test password
        if check_password('student123', student.password):
            print("✓ Student password is correct")
        else:
            print("✗ Student password is incorrect")
            
        # Test authentication
        auth_user = authenticate(username='student', password='student123')
        if auth_user:
            print("✓ Student authentication works")
        else:
            print("✗ Student authentication failed")
            
    except User.DoesNotExist:
        print("✗ Student user not found")
    
    print("\n=== Testing URL Patterns ===")
    
    # Test 4: Check if all required URLs are accessible
    from django.urls import reverse
    from django.test import Client
    
    client = Client()
    
    # Test login page
    try:
        response = client.get('/login/')
        if response.status_code == 200:
            print("✓ Login page accessible")
        else:
            print(f"✗ Login page returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Login page error: {e}")
    
    # Test instructor dashboard
    try:
        response = client.get('/courses/instructor/dashboard/')
        if response.status_code == 302:  # Should redirect to login
            print("✓ Instructor dashboard redirects to login (expected)")
        else:
            print(f"✗ Instructor dashboard returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Instructor dashboard error: {e}")
    
    print("\n=== Testing Template Files ===")
    
    # Test 5: Check if all template files exist
    template_files = [
        'src/web/website/templates/website/unified_login.html',
        'templates/instructor/dashboard.html',
        'templates/instructor/courses.html',
        'templates/instructor/students.html',
        'templates/instructor/profile.html',
        'templates/instructor/course_detail.html',
        'src/web/website/templates/website/include/header.html',
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"✓ {template_file} exists")
        else:
            print(f"✗ {template_file} missing")
    
    print("\n=== Testing Model Methods ===")
    
    # Test 6: Check instructor model methods
    try:
        instructor = Instructor.objects.first()
        if instructor:
            print(f"✓ Instructor model has {instructor.get_courses_count()} courses")
            print(f"✓ Instructor model has {instructor.get_total_students()} total students")
            print(f"✓ Instructor model has {instructor.get_active_students()} active students")
            print(f"✓ Instructor model has {instructor.get_trial_students()} trial students")
        else:
            print("✗ No instructor found for testing")
    except Exception as e:
        print(f"✗ Instructor model test error: {e}")
    
    print("\n=== Summary ===")
    print("All tests completed. Check the results above for any issues.")

if __name__ == "__main__":
    test_login_system()
