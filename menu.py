import os
import sys
import subprocess
from pathlib import Path

from art import LOGO

ROOT = Path(__file__).parent


def main() -> None:
    clear = True
    while True:
        if clear:
            os.system("cls" if os.name == "nt" else "clear")
        clear = True

        print(LOGO)
        print("Select a build to run:")
        print("  1) Original  — course script (Nutritionix + Sheety, non-functional)")
        print("  2) Advanced  — OOP refactor with Ollama + Sheety")
        print("  q) Quit")
        print()

        choice = input("Enter choice: ").strip().lower()

        if choice == "1":
            path = ROOT / "original" / "main.py"
            subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
            input("\nPress Enter to return to menu...")
        elif choice == "2":
            path = ROOT / "advanced" / "main.py"
            subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
        elif choice == "q":
            break
        else:
            print("Invalid choice. Try again.")
            clear = False


if __name__ == "__main__":
    main()
