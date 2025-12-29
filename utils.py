from datetime import datetime
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
from dotenv import load_dotenv
from constant import CLASS_STUDENT_MAP
load_dotenv()


# --- Configuration ---
LOGIN_URL = os.getenv("LOGIN_URL")
DASHBOARD_URL = os.getenv("DASHBOARD_URL")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
PASSWORD = os.getenv("PASSWORD")
MATERIAL_NOTES = os.getenv("MATERIAL_NOTES")
TEACHER_CODE = os.getenv("TEACHER_CODE")
SUBJECT_NAME = os.getenv("SUBJECT_NAME")
SUBJECT_PROPER_NAME = os.getenv("SUBJECT_PROPER_NAME")
# ----------------------

class GradeAutomator:
    """
    Automates the process of logging into a web portal, navigating to the
    grade submission section, and creating or updating student grades based
    on data from an Excel file.
    """
    def __init__(self, ASSESSMENT_URL, assessment_type="harian", assessment_number=None, excel_path=""):
        self.login_url = LOGIN_URL
        self.phone_number = PHONE_NUMBER
        self.excel_path = excel_path
        self.assessment_url = ASSESSMENT_URL
        self.material_notes = MATERIAL_NOTES
        self.teacher_code = TEACHER_CODE
        self.subject_name = SUBJECT_NAME
        self.class_student_map = CLASS_STUDENT_MAP
        self.driver = None
        self.df = None
        self.assessment_type = assessment_type
        self.assessment_number = assessment_number

    def _setup_driver(self):
        """Sets up the Selenium WebDriver."""
        print("Setting up Chrome WebDriver...")
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)

    def _load_data(self):
        """Loads student data from the Excel file."""
        try:
            self.df = pd.read_excel(self.excel_path)
            if self.df.empty:
                raise ValueError(f"Excel file '{self.excel_path}' is empty.")
        except FileNotFoundError:
            print(f"Error: The file '{self.excel_path}' was not found.")
            raise
        except Exception as e:
            print(f"An error occurred while reading the Excel file: {e}")
            raise

    def _login(self):
        """Handles the login process."""
        print(f"Navigating to login page: {self.login_url}")
        self.driver.get(self.login_url)

        print(f"Entering phone number: {self.phone_number}")
        username_input = self.driver.find_element(By.ID, "nohp")
        username_input.send_keys(self.phone_number)
        print(f"Entering password .......")
        username_input = self.driver.find_element(By.NAME, "password")
        username_input.send_keys(PASSWORD)

        sign_in_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        sign_in_button.click()
        print("Login form submitted. Waiting for manual OTP verification...")

        try:
            WebDriverWait(self.driver, 300).until(EC.url_contains("dashboard"))
            print("Login successful! Redirected to the dashboard.")
            return True
        except TimeoutException:
            print("Login failed or took too long. Exiting.")
            return False

    def _fill_assessment_details(self, class_name):
        """Fills the first form on the 'nilai-harian-list' page."""
        print("Navigating to 'nilai-harian-list' page...")
        current_url = self.driver.current_url
        kdx = current_url.split('kdx=')[1]
        assessment_url = f"{self.assessment_url}?kdx={kdx}"
        
        print(f"Navigating to assessment page: {assessment_url}")
        self.driver.get(assessment_url)

        print("Filling assessment details...")
        Select(self.driver.find_element(By.ID, "tanggal_k")).select_by_value(str(datetime.now().day))
        Select(self.driver.find_element(By.ID, "bulan_k")).select_by_value(str(datetime.now().month))
        Select(self.driver.find_element(By.ID, "tahun_k")).select_by_value(str(datetime.now().year))
        print(f"Date set to: {datetime.now().day}-{datetime.now().month}-{datetime.now().year}")

        mapel_select = Select(self.driver.find_element(By.ID, "mapel_k"))
        mapel_select.select_by_value(f'{self.teacher_code}{self.subject_name.lower()}{class_name}')
        print(f"Subject/Class selected.")

        if (self.assessment_number is not None) and (self.assessment_type == "harian"):
            Select(self.driver.find_element(By.ID, "penilaian_ke")).select_by_value(str(self.assessment_number))
            print(f"Assessment number set to: {self.assessment_number}")

        self.driver.find_element(By.ID, "materi").send_keys(self.material_notes)
        print(f"Materi set to: {self.material_notes}")

        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("Assessment details form submitted.")

    def _fill_student_grades(self, numbers, class_name):
        """Fills the grades for each student on the 'nilai-harian-input' page."""
        print("Waiting for the student list to load...")
        try:
            if self.assessment_type == "harian":
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "form[action*='kbmnilaiinputproses']"))
                )
            elif self.assessment_type == "ikhtibar_nihaiy":
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "form[action*='kbmnilaiinputpsastproses']"))
                )
            else:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "form[action*='kbmnilaiinputpstsproses']"))
                )
            print("Student list loaded. Filling grades...")
        except TimeoutException:
            print("Could not find the student grades form. The previous step might have failed.")
            return

        student_rows = self.driver.find_elements(By.CSS_SELECTOR, "form .row.mb-3.align-items-center")

        if not student_rows:
            print("No student rows found to input grades.")
            return
        
        filtered_df = self.df[self.df["Kelas"] == str(class_name)]

        if len(student_rows) > numbers:
            print(f"Warning! Found {len(student_rows)} students in {class_name}, but expected {numbers} students.")
            
        print(f"Found {len(student_rows)} students. Assigning grades.")
        for i in range(len(filtered_df)):
            try:
                student_id = filtered_df.iloc[i].iloc[2]
                grade = filtered_df.iloc[i].iloc[5]
                notes = filtered_df.iloc[i].iloc[6]
                self.driver.find_element(By.ID, f"nilai{student_id}").send_keys(str(round(grade)))
                self.driver.find_element(By.ID, f"catatan{student_id}").send_keys(notes if pd.notna(notes) else "")
            except Exception as e:
                print(f"Could not fill grade for student {i+1}. Error: {e}")

        print("Submitting all grades...")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", submit_button)
        print("Grades submitted successfully!")

    def _update_student_grades(self, numbers, class_name):
        """Updates the grades for each student on the 'kbmnilaiinputedit' page."""
        print("Waiting for the student list to load for editing...")
        try:
            if self.assessment_type == "harian":
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "form[action*='kbmnilaiinputeditproses']"))
                )
            elif self.assessment_type == "ikhtibar_nihaiy":
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "form[action*='kbmnilaiinputeditpsastproses']"))
                )
            else:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "form[action*='kbmnilaiinputeditpstsproses']"))
                )
            print("Student list loaded for editing. Updating grades...")
        except TimeoutException:
            print("Could not find the student grades form for editing.")
            return

        materi = self.driver.find_element(By.NAME, "materi")
        materi.clear()
        materi.send_keys(self.material_notes)

        student_rows = self.driver.find_elements(By.CSS_SELECTOR, "form .row.mb-3.align-items-center")
        if not student_rows:
            print("No student rows found to update.")
            return
        
        filtered_df = self.df[self.df["Kelas"] == str(class_name)]

        if len(student_rows) > numbers:
            print(f"Found {len(student_rows)} students in {class_name}, but expected {numbers} students.")

        print(f"Found {len(student_rows)} students. Updating grades.")
        for i in range(len(filtered_df)):
            try:
                student_id = filtered_df.iloc[i].iloc[2]
                grade = filtered_df.iloc[i].iloc[5]
                notes = filtered_df.iloc[i].iloc[6]
                grade_input = self.driver.find_element(By.NAME, f"nilai{student_id}")
                grade_input.clear()
                grade_input.send_keys(str(round(grade)))
                notes_input = self.driver.find_element(By.NAME, f"catatan{student_id}")
                notes_input.clear()
                notes_input.send_keys(notes if pd.notna(notes) else "")
            except Exception as e:
                print(f"Could not update grade for student {i+1}. Error: {e}")

        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", submit_button)
        print("Grades updated successfully!")

    def run(self):
        """Main function to run the automation script."""
        try:
            self._load_data()
            self._setup_driver()
            if self._login():
                for numbers, class_name in self.class_student_map:
                    print(f"Processing class: {class_name} with {numbers} students.")
                    self._fill_assessment_details(class_name)
                    sleep(2)

                    if "Notifikasi" in self.driver.title:
                        print("Assessment already exists. Switching to update mode.")
                        current_url = self.driver.current_url
                        kdx = current_url.split('kdx=')[1] if 'kdx=' in current_url else self.teacher_code
                        assessment_url = f"{self.assessment_url}?kdx={kdx}"
                        self.driver.get(assessment_url)
                        
                        wait = WebDriverWait(self.driver, 5)
                        search_input = wait.until(EC.visibility_of_element_located((
                            By.CSS_SELECTOR,
                            "input[type='search'][aria-controls='tabelNilaiHarian']"
                        )))
                        search_input.clear()
                        search_input.send_keys(f"{class_name}")
                        wait = WebDriverWait(self.driver, 5)


                        if self.assessment_type == "harian":
                            edit_button = wait.until(EC.element_to_be_clickable((
                                By.XPATH,
                                f"//tr[td[normalize-space()='{class_name}'] and td[normalize-space()='{SUBJECT_PROPER_NAME}']]//a[contains(@href, 'kbmnilaiinputedit')]"
                            )))
                        elif self.assessment_type == "ikhtibar_nihaiy":
                            edit_button = wait.until(EC.element_to_be_clickable((
                                By.XPATH,
                                f"//tr[td[normalize-space()='{class_name}'] and td[normalize-space()='{SUBJECT_PROPER_NAME}']]//a[contains(@href, 'kbmnilaiinputpsastedit')]"
                            )))
                        else:
                            edit_button = wait.until(EC.element_to_be_clickable((
                                By.XPATH,
                                f"//tr[td[normalize-space()='{class_name}'] and td[normalize-space()='{SUBJECT_PROPER_NAME}']]//a[contains(@href, 'kbmnilaiinputpstsedit')]"
                            )))
                        
                        self.driver.execute_script("arguments[0].click();", edit_button)
                        self._update_student_grades(numbers, class_name)
                    else:
                        self._fill_student_grades(numbers, class_name)
                    sleep(5)
                print("Automation script finished.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            if self.driver:
                print("Closing browser in 15 seconds...")
                sleep(15)
                self.driver.quit()