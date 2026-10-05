"""
main.py - Run this file to start JARVIS.

Keep main.py, features_module.py and askai.py in the same folder.
"""

from features_module import process_command, listen, say


def main():
    say("Jarvis is online. How can I help you?")

    while True:
        try:
            text = listen()
            if not text:
                continue  # silence or unclear speech - listen again

            response = process_command(text)
            if response:
                print("Jarvis:", response)
                say(response)  # spoken once, here only

        except KeyboardInterrupt:
            print("\nStopped by user.")
            break
        except Exception as e:
            print(f"Error: {e}")
            say("Sorry, something went wrong.")


if __name__ == "__main__":
    main()
