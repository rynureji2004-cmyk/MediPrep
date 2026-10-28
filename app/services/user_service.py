import bcrypt
from app.repositories.user_repository import UserRepository
from app.utilities.validators import validate_password_strength
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Handles credentials hashing, comparison, and verification operations."""


    @staticmethod
    def register_user(username, email, password, first_name, last_name, role_name, phone=None, profile_data=None):
        """
        Registers a new user, hashes their password, and sets up their role profile.
        Returns the user ID on success, or raises ValueError.
        """
        # Validate uniqueness
        if UserRepository.username_exists(username):
            raise ValueError("Username already exists.")
        if UserRepository.email_exists(email):
            raise ValueError("Email address is already registered.")
        
        # Get role ID
        role_id = UserRepository.get_role_id_by_name(role_name)
        if not role_id:
            raise ValueError(f"Role '{role_name}' does not exist.")
        
        # Hash password using bcrypt
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        user_data = {
            'role_id': role_id,
            'role_name': role_name,
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone
        }
        
        return UserRepository.create_user_transaction(user_data, profile_data)

    @staticmethod
    def authenticate_user(username_or_email, password):
        """
        Verifies login credentials.
        Checks both username and email fields.
        Returns user dictionary if authenticated, otherwise None.
        """
        if not username_or_email or not password:
            return None

        identifier = str(username_or_email).strip()

        # Try finding by username first, then email
        user = UserRepository.find_by_username(identifier)
        if not user:
            user = UserRepository.find_by_email(identifier)
            
        if not user:
            logger.info(f"Failed authentication attempt: User '{identifier}' not found.")
            return None
            
        # Verify hash matches password
        raw_hash = user['password_hash']
        password_hash = raw_hash.encode('utf-8') if isinstance(raw_hash, str) else raw_hash
        raw_pw = password.encode('utf-8') if isinstance(password, str) else password

        if bcrypt.checkpw(raw_pw, password_hash):
            logger.info(f"User '{user['username']}' authenticated successfully.")
            return {
                'id': user['id'],
                'role_id': user['role_id'],
                'role_name': user['role_name'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }
        else:
            logger.info(f"Failed authentication attempt: Incorrect password for '{user['username']}'.")
            return None
            
    @staticmethod
    def get_user_by_id(user_id):
        """Retrieves user info from the database."""
        return UserRepository.find_by_id(user_id)

    @staticmethod
    def reset_user_password(user_id, new_password):
        """
        Validates password strength, hashes it using bcrypt, and updates the user's password in DB.
        """
        if not validate_password_strength(new_password):
            raise ValueError("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character (@$!%*?&#).")

        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
        
        return UserRepository.update_password(user_id, password_hash)

