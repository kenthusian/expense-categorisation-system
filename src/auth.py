import pandas as pd  # type: ignore
import hashlib
import os

USERS_FILE = "users.csv"

def hash_password(password):
    """
    Hashes a password using SHA-256.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """
    Loads users from the CSV file. Creates it if missing.
    """
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=["username", "password"])
        df.to_csv(USERS_FILE, index=False)
        return df
    return pd.read_csv(USERS_FILE)

def signup_user(username, password):
    """
    Signs up a new user. Returns (success, message).
    """
    df = load_users()
    if username in df["username"].values:
        return False, "Username already exists."
    
    hashed_pw = hash_password(password)
    # Create a new DataFrame for the new user
    new_user = pd.DataFrame([[username, hashed_pw]], columns=["username", "password"])
    # Concatenate the new user DataFrame with the existing one
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)
    return True, "User registered successfully!"

def login_user(username, password):
    """
    Logins a user. Returns (success, message).
    """
    df = load_users()
    hashed_pw = hash_password(password)
    
    user_row = df[df["username"] == username]
    if user_row.empty:
        return False, "User not found."
    
    if user_row["password"].values[0] == hashed_pw:
        return True, f"Welcome back, {username}!"
    else:
        return False, "Incorrect password."
