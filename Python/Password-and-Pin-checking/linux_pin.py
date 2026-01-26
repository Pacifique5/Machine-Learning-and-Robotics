import subprocess

def check_pin(username, pin):
    try:
        # Invalidate user's cached credentials
        subprocess.run(['sudo', '-k'])

        # Try to authenticate using the provided PIN (treated like a password)
        result = subprocess.run(['sudo', '-S', 'echo', 'Authenticated'],
                                input=pin.encode(),
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        
        if 'Authenticated' in result.stdout.decode():
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