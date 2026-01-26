import subprocess

def check_password(username, password):
    try:
        # Invalidate user's cached credentials
        subprocess.run(['sudo', '-k'])

        # Try to authenticate using the provided password
        result = subprocess.run(['sudo', '-S', 'echo', 'Authenticated'],
                                input=password.encode(),
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
password = input("Enter your password: ")

if check_password(username, password):
    print("Password is correct.")
else:
    print("Password is incorrect.")