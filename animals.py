import random

print("Hi This is a guessing game where you have 9 lives !!!")

words = ['snake', 'tiger', 'panda', 'zebra', 'rhino']

lives = 9
word = random.choice(words)
clue = ['?'] * len(word)
guessed_letters = []

print("\nLet's start!")

while lives > 0 and '?' in clue:
    print("\n[" + " ".join(clue) + "]")
    print("Lives left: " + "❤ " * lives)
    print("Guessed letters:", ", ".join(guessed_letters) if guessed_letters else "None")
    
    input_letter = input("Guess a letter: ").lower()
    
    # Validate input
    if len(input_letter) != 1 or not input_letter.isalpha():
        print("Please enter a single letter!")
        continue
    
    if input_letter in guessed_letters:
        print("You already guessed that letter!")
        continue
    
    guessed_letters.append(input_letter)
    
    if input_letter in word:
        for index, letter in enumerate(word):
            if letter == input_letter:
                clue[index] = input_letter
        print("Correct! ✓")
    else:
        lives -= 1
        print("Wrong! ✗")

# Game over
print("\n" + "=" * 40)
if '?' not in clue:
    print("🎉 Congratulations! You won!")
    print("The word was:", word)
else:
    print("💀 Game Over! You ran out of lives.")
    print("The word was:", word)
print("=" * 40)