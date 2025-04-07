import pyrebase

firebase_config = {
    "apiKey": "AIzaSyANdM_otPBpOSAv4pdKDSiazqwT0Ep06gw",
    "authDomain": "glean-eggs.firebaseapp.com",
    "databaseURL": "",  
    "projectId": "glean-eggs",
    "storageBucket": "glean-eggs.appspot.com",  
    "messagingSenderId": "1017377888411",
    "appId": "1:1017377888411:web:fb7174890943bdc4fa8e3e",
}


firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()


def signup(email, password):
    try:
        user = auth.create_user(email, password)
        print("User created successfully!")
        return user
    except Exception as e:
        print(f"Error: {e}")


def login(email, password):
    try:
        user = auth.sign_in(email, password)
        print("Login successful!")
        print("User Token:", user['idToken'])
        return user
    except Exception as e:
        print(f"Error: {e}")


def get_user_info(user):
    try:
        info = auth.get_account_info(user['idToken'])
        print("User Info:", info)
    except Exception as e:
        print(f"Error: {e}")


def logout():
    print("User logged out!")


if __name__ == "__main__":
    print("Welcome to Glean Eggs")
    
    while True:
        print("\nOptions:")
        print("1. Sign Up")
        print("2. Log In")
        print("3. Exit")
        
        choice = input("Enter your choice: ")

        if choice == "1":
            email = input("Enter email: ")
            password = input("Enter password: ")
            user = signup(email, password)
            print("Signed up successfully!" if user else "Sign-up failed.")
        
        elif choice == "2":
            email = input("Enter email: ")
            password = input("Enter password: ")
            user = login(email, password)
            if user:
                get_user_info(user)
        
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
