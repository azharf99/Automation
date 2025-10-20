# Grade Submission Automation

This project contains a Python automation script that uses Selenium to log into the Albinaa school portal (`jurnal.albinaa.ponpes.id`) and submit student grades for various assessments. It reads grade data from an Excel file and can handle both creating new grade entries and updating existing ones.

## Features

- **Automated Login**: Logs into the portal using credentials from a secure `.env` file. It waits for the user to manually complete OTP verification.
- **Data-Driven**: Populates grades from a structured Excel file, making it easy to manage large amounts of data.
- **Multiple Assessment Types**: The structure supports different types of assessments, such as daily assessments (`harian.py`) and mid-term exams (`pts.py`).
- **Create or Update Logic**: Intelligently checks if a grade entry for a specific class and assessment already exists. If it does, it updates the grades; otherwise, it creates a new entry.
- **Configurable**: Key settings like URLs, file paths, and credentials are managed through a `.env` file for security and ease of modification.
- **Modular and OOP Design**: The core logic is encapsulated in a `GradeAutomator` class (`utils.py`), making the code clean, reusable, and easy to maintain.

## Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.11** or newer.
- **Google Chrome** browser.

## Setup and Installation

Follow these steps to get your development environment set up.

### 1. Clone the Repository

First, clone the repository to your local machine.

```bash
git clone <your-repository-url>
cd <repository-directory>
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

**On Windows:**
```bash
python -m venv env
.\env\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

Install all the required Python packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

This will install `selenium`, `pandas`, `openpyxl`, and other necessary libraries. `webdriver-manager` will automatically handle the `chromedriver` for you.

### 4. Configure Environment Variables

Create a `.env` file in the root directory by copying the example file.

```bash
copy .env.example .env
```

Now, open the `.env` file and fill in the required values.

```ini
# .env
LOGIN_URL="url target login"
DASHBOARD_URL="url target dashboard"

# URLs for different assessment types
DAILY_ASSESSMENT_URL="url target nilai harian"
IKHTIBAR_NISFI_URL="url target ikhtibar nisfi"

# Credentials and Teacher Info
PHONE_NUMBER="your_phone_number"
TEACHER_CODE="your_teacher_code"
SUBJECT_NAME="your_subject_name" # e.g., biologi

# File Paths for Grade Data
DAILY_ASSESSMENT_FILE_PATH="path/to/your/daily_grades.xlsx"
IKHTIBAR_NISFI_FILE_PATH="path/to/your/midterm_grades.xlsx"

# Assessment Details
MATERIAL_NOTES="Topic of the material being assessed"
ASSESSMENT_NUMBER="1" # The number for the daily assessment (e.g., 1, 2, 3)
```

### 5. Prepare the Grade Data File

Use the `template.xlsx` file as a reference to create your grade data files. The script expects the Excel file to have a specific structure. The important columns are:
- `Kelas`: The class name (e.g., "X-A").
- Column at index `2`: The unique student ID used in the portal's form elements.
- Column at index `5`: The numerical grade for the student.

Make sure your Excel files (`daily_grades.xlsx`, `midterm_grades.xlsx`, etc.) are correctly formatted and placed in the location specified in your `.env` file.

## Running the Script

Once everything is set up, you can run the automation scripts. Make sure your virtual environment is activated.

### To Run the Daily Assessment (`harian`)

```bash
python harian.py
```

### To Run the Mid-term Assessment (`pts`)

```bash
python pts.py
```

The script will open a Chrome browser, navigate to the login page, and wait for you to enter the OTP. After successful login, it will proceed to automate the grade submission process.