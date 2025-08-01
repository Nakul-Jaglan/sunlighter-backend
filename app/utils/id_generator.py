import random
import string
from sqlalchemy.orm import Session
from app.models.user import User


def generate_employee_user_id(db: Session) -> str:
    """
    Generate a 6-digit alphanumeric user ID for employees.
    Format: alphanumeric, no leading zeros (e.g., Z2DU79, A1B2C3)
    """
    while True:
        # Start with a letter to avoid leading zeros
        first_char = random.choice(string.ascii_uppercase)
        # Generate 5 more characters (letters and numbers)
        remaining_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        user_id = first_char + remaining_chars
        
        # Check if this user_id already exists
        existing = db.query(User).filter(User.user_id == user_id).first()
        if not existing:
            return user_id


def generate_employer_id(db: Session) -> int:
    """
    Generate a numeric employer ID between 100000 and 999999 for internal use.
    """
    while True:
        employer_id = random.randint(100000, 999999)
        
        # Check if this employer_id already exists
        existing = db.query(User).filter(User.employer_id == employer_id).first()
        if not existing:
            return employer_id


def generate_company_handle(company_name: str, db: Session) -> str:
    """
    Generate a company handle from company name.
    Format: @companyname (lowercase, no spaces)
    If exists, append numbers: @companyname1, @companyname2, etc.
    """
    # Clean company name: lowercase, remove spaces and special chars
    base_handle = ''.join(c.lower() for c in company_name if c.isalnum())
    
    # Limit length to 20 characters
    base_handle = base_handle[:20]
    
    counter = 0
    while True:
        if counter == 0:
            handle = base_handle
        else:
            handle = f"{base_handle}{counter}"
        
        # Check if this handle already exists
        existing = db.query(User).filter(User.company_handle == handle).first()
        if not existing:
            return handle
        
        counter += 1
        # Prevent infinite loop
        if counter > 999:
            # Fallback with random suffix
            random_suffix = ''.join(random.choices(string.digits, k=3))
            return f"{base_handle}{random_suffix}"
