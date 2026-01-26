import ctypes

def check_password(username, password, domain=''):
    try:
        # Attempt to log in with provided credentials
        result = ctypes.windll.advapi32.LogonUserW(
            username, domain, password,
            3, 0, ctypes.byref(ctypes.c_void_p())
        )
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Example usage
username = input("Enter your username: ")
password = input("Enter your password: ")

if check_password(username, password):
    print("Password is correct.")
else:
    print("Password is incorrect.")