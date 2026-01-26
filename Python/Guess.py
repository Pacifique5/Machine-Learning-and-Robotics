import random

def number_guessing_game():
    random_number = random.randint(1, 100)
    attempts = 0
    
    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")
    
    while True:
        attempts += 1
        try:
            user_guess = int(input("Enter your guess: "))
        except ValueError:
            print("Please enter a valid number.")
            continue
            
        if user_guess == random_number:
            print(f"Congratulations! You guessed it in {attempts} attempts!")
            break
        elif user_guess < random_number:
            print("Too low! Try again.")
        else:
            print("Too high! Try again.")

# Run the game
number_guessing_game()