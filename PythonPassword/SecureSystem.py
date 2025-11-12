import bcrypt
import os

USER_DATA_FILE = "users.txt"

def hash_password(plain_text_password):
    # Encode the password to bytes (bcrypt requires byte strings)
    password_bytes = plain_text_password.encode('utf-8')
    # Generate a salt using bcrypt.gensalt()
    salt = bcrypt.gensalt()
    # Hash the password using bcrypt.hashpw()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Decode the hash back to a string to store in a text file
    return hashed.decode('utf-8')

def verify_password(plain_text_password, hashed_password):
    # Encode both the plaintext password and the stored hash to bytes
    password_bytes = plain_text_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    # Use bcrypt.checkpw() to verify the password
    # This function extracts the salt from the hash and compares
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def register_user(username, password):
    # Check if the username already exists
    if user_exists(username):
        return False
    # Hash the password
    hashed = hash_password(password)
    # Append the new user to the file
    # Format: username,hashed_password
    with open(USER_DATA_FILE, 'a') as f:
        f.write(f"{username},{hashed}\n")
    return True

def user_exists(username):
    # Handle the case where the file doesn't exist yet
    if not os.path.exists(USER_DATA_FILE):
        return False
    # Read the file and check each line for the username
    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            stored_username, _ = line.strip().split(',')
            if stored_username == username:
                return True
    return False

def login_user(username, password):
    # Handle the case where no users are registered yet
    if not os.path.exists(USER_DATA_FILE):
        return False
    # Search for the username in the file
    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            stored_username, stored_hash = line.strip().split(',')
            if stored_username == username:
                # If username matches, verify the password
                return verify_password(password, stored_hash)
    # If we reach here, the username was not found
    return False

def validate_username(username):
    if not username:
        return False, "Username cannot be empty."
    if not username.isalnum():
        return False, "Username must be alphanumeric."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    return True, ""

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    return True, ""

def display_menu():
    """Displays the main menu options."""
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")
    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()
        if choice == '1':
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()
            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
            password = input("Enter a password: ").strip()
            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue
            # Register the user
            if register_user(username, password):
                print("Registration successful!")
            else:
                print("Username already exists.")
        elif choice == '2':
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()
            # Attempt login
            if login_user(username, password):
                print("\nYou are now logged in.")
                print("(In a real application, you would now access the dashboard)")
                # Optional: Ask if they want to logout or exit
                input("\nPress Enter to return to main menu...")
            else:
                print("Invalid username or password.")
        elif choice == '3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break
        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
