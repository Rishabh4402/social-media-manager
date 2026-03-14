import sys
import os

# Ensure the root directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent.core import InstagramAgent

def main():
    agent = InstagramAgent()
    agent.run()

if __name__ == "__main__":
    main()
