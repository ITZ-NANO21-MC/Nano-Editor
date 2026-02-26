
import random

def play_game():
    choices = ["piedra", "papel", "tijeras"]
    user_choice = input("Elige piedra, papel o tijeras: ").lower()

    while user_choice not in choices:
        user_choice = input("Opción inválida. Elige piedra, papel o tijeras: ").lower()

    bot_choice = random.choice(choices)

    print(f"Tú elegiste: {user_choice}")
    print(f"El bot eligió: {bot_choice}")

    if user_choice == bot_choice:
        print("¡Es un empate!")
    elif (user_choice == "piedra" and bot_choice == "tijeras") or \
         (user_choice == "papel" and bot_choice == "piedra") or \
         (user_choice == "tijeras" and bot_choice == "papel"):
        print("¡Ganaste!")
    else:
        print("¡Perdiste!")

if __name__ == "__main__":
    play_game()
