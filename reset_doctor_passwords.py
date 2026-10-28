"""
MediPrep Doctor Password Management & Reset Utility
====================================================
Safely resets or verifies doctor credentials using the existing
application architecture (UserService, Bcrypt 12 rounds).
Preserves all foreign keys, doctor profiles, and specialty records.
"""

import sys
import os

# Add root folder to sys path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

DOCTOR_ACCOUNTS = [
    'doctor_robert',
    'doctor_anil',
    'doctor_priya',
    'doctor_rahul',
    'doctor_sneha'
]

def verify_doctor_logins(password="Password123!"):
    """Verifies login credentials for all doctor accounts."""
    app = create_app('development')
    with app.app_context():
        print(f"\nVerifying Doctor Logins against password: '{password}'")
        print("-" * 65)
        all_passed = True
        for username in DOCTOR_ACCOUNTS:
            user = UserService.authenticate_user(username, password)
            if user:
                print(f"[OK] {username:15} | ID: {user['id']:2} | Role: {user['role_name']} | Dr. {user['first_name']} {user['last_name']}")
            else:
                print(f"[FAIL] {username:15} | Could not authenticate with provided password.")
                all_passed = False
        print("-" * 65)
        return all_passed

def reset_doctor_passwords(password_map):
    """
    Safely resets passwords using UserService.reset_user_password.
    password_map: dict of {username: new_password}
    """
    app = create_app('development')
    with app.app_context():
        print("\nExecuting Safe Doctor Password Reset")
        print("=" * 65)
        reset_results = {}
        for username, new_pw in password_map.items():
            user = UserRepository.find_by_username(username)
            if not user:
                print(f"[ERROR] User '{username}' not found in database.")
                continue
            
            # Use application's UserService to ensure strength validation and proper 12-round bcrypt hash
            success, msg = UserService.reset_user_password(user['id'], new_pw)
            if success:
                # Immediate verification
                verified = UserService.authenticate_user(username, new_pw)
                if verified:
                    print(f"[SUCCESS & VERIFIED] {username:15} -> Password updated and login confirmed.")
                    reset_results[username] = True
                else:
                    print(f"[WARNING] {username:15} -> Password updated but authentication verification failed.")
                    reset_results[username] = False
            else:
                print(f"[ERROR] {username:15} -> Reset failed: {msg}")
                reset_results[username] = False
        print("=" * 65)
        return reset_results

if __name__ == '__main__':
    # Default execution: verify existing credentials
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        pw = sys.argv[2] if len(sys.argv) > 2 else "Password123!"
        verify_doctor_logins(pw)
    else:
        print("Doctor Password Management Tool")
        print("Usage:")
        print("  python reset_doctor_passwords.py --verify [password]")
        verify_doctor_logins("Password123!")
