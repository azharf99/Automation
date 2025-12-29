import os
from utils import GradeAutomator
from dotenv import load_dotenv
load_dotenv()

IKHTIBAR_NIHAIY_URL = os.getenv("IKHTIBAR_NIHAIY_URL")
IKHTIBAR_NIHAIY_FILE_PATH = os.getenv("IKHTIBAR_NIHAIY_FILE_PATH")

def main():
    """Initializes and runs the GradeAutomator."""
    automator = GradeAutomator(IKHTIBAR_NIHAIY_URL, "ikhtibar_nihaiy", excel_path=IKHTIBAR_NIHAIY_FILE_PATH)
    automator.run()

if __name__ == "__main__":
    main()