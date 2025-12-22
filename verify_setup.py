import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

try:
    from main import app
    from db.session import engine
    from schemas.test import Test
    from crud import crud_test
    print("Imports successful!")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)
