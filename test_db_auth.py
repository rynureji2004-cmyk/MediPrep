import sys
import os

# Add root folder to sys path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from app.services.user_service import UserService
from config import config_by_name

def run_tests():
    print("=== MediPrep Authentication Integration Test ===")
    
    # Load development config
    config = config_by_name['development']
    
    # Initialize Database pool
    print(f"Initializing connection pool on {config.DB_HOST} ({config.DB_NAME})...")
    try:
        DatabaseManager.initialize_pool(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            pool_size=2,
            pool_name='test_pool'
        )
    except Exception as e:
        print(f"ERROR initializing connection pool: {e}")
        print("Please check that your MySQL server is running and database 'hospital_readiness_db' is created.")
        return False
        
    # Attempt to authenticate doctor_robert
    username = "doctor_robert"
    password = "Password123!"
    
    print(f"\nAttempting authentication for '{username}' with password '{password}'...")
    try:
        user = UserService.authenticate_user(username, password)
        if user:
            print("SUCCESS! User authenticated.")
            print(f"User Details: ID={user['id']}, Name={user['first_name']} {user['last_name']}, Role={user['role_name']}")
        else:
            print("FAILED: Authentication returned None (check if user exists and password hash matches).")
    except Exception as e:
        print(f"ERROR during authentication verification: {e}")
        return False
        
    # Attempt to authenticate patient_john
    username = "patient_john"
    password = "Password123!"
    
    print(f"\nAttempting authentication for '{username}' with password '{password}'...")
    try:
        user = UserService.authenticate_user(username, password)
        if user:
            print("SUCCESS! User authenticated.")
            print(f"User Details: ID={user['id']}, Name={user['first_name']} {user['last_name']}, Role={user['role_name']}")
        else:
            print("FAILED: Authentication returned None.")
    except Exception as e:
        print(f"ERROR: {e}")
        return False

    # Test dynamic registration
    print("\nTesting Registration of a new Patient...")
    reg_username = "patient_test_user"
    reg_email = "test.patient@hospital.org"
    reg_pw = "StrongPass123!"
    
    profile_data = {
        'date_of_birth': '1995-04-12',
        'gender': 'female',
        'blood_type': 'O+',
        'medical_history': 'None reported',
        'emergency_contact_name': 'Test Contact',
        'emergency_contact_phone': '+15559988'
    }
    
    try:
        new_uid = UserService.register_user(
            username=reg_username,
            email=reg_email,
            password=reg_pw,
            first_name="Test",
            last_name="Patient",
            role_name="patient",
            phone="+15559977",
            profile_data=profile_data
        )
        print(f"SUCCESS! New user registered with ID: {new_uid}")
        
        # Test authenticating new user
        print(f"Verifying login for newly registered user '{reg_username}'...")
        verified_user = UserService.authenticate_user(reg_username, reg_pw)
        if verified_user:
            print(f"SUCCESS! Logged in new patient. Role: {verified_user['role_name']}")
        else:
            print("FAILED: Newly registered user could not login.")
    except ValueError as val_err:
        print(f"VALUE ERROR: {val_err} (Is user already registered from a previous test run?)")
    except Exception as e:
        print(f"REGISTRATION ERROR: {e}")
        
    print("\n=== Test Verification Completed ===")

if __name__ == '__main__':
    run_tests()
