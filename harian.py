import os
from utils import GradeAutomator
from dotenv import load_dotenv
load_dotenv()

DAILY_ASSESSMENT_URL = os.getenv("DAILY_ASSESSMENT_URL")
ASSESSMENT_NUMBER = os.getenv("ASSESSMENT_NUMBER")
DAILY_ASSESSMENT_FILE_PATH = os.getenv("DAILY_ASSESSMENT_FILE_PATH")

def main():
    """Initializes and runs the GradeAutomator."""
    automator = GradeAutomator(DAILY_ASSESSMENT_URL, "harian", ASSESSMENT_NUMBER, DAILY_ASSESSMENT_FILE_PATH)
    automator.run()

if __name__ == "__main__":
    main()