import sys
import os
from scripts.run_bills import main as bills_main
from scripts.run_server import main as server_main

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [bills|server] [args...]")
        return

    command = sys.argv[1]
    
    # Shift args so the sub-scripts see their expected arguments
    sys.argv.pop(1)
    
    if command == "bills":
        bills_main()
    elif command == "server":
        server_main()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: bills, server")

if __name__ == "__main__":
    main()
