import os
from utils import GradeAutomator
from dotenv import load_dotenv
load_dotenv()

IKHTIBAR_NISFI_URL = os.getenv("IKHTIBAR_NISFI_URL")
IKHTIBAR_NISFI_FILE_PATH = os.getenv("IKHTIBAR_NISFI_FILE_PATH")

def main():
    """Initializes and runs the GradeAutomator."""
    automator = GradeAutomator(IKHTIBAR_NISFI_URL, "ikhtibar_nisfi", excel_path=IKHTIBAR_NISFI_FILE_PATH)
    automator.run()

if __name__ == "__main__":
    main()