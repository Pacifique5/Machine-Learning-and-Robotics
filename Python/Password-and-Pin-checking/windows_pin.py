import ctypes

def check_pin(username, pin, domain=''):
    try:
        # Attempt to log in with provided credentials (assuming PIN is treated as password)
        result = ctypes.windll.advapi32.LogonUserW(
            username, domain, pin,
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
pin = input("Enter your PIN: ")

if check_pin(username, pin):
    print("PIN is correct.")
else:
    print("PIN is incorrect.")