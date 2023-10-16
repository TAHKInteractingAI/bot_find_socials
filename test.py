import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook, load_workbook
from bs4 import BeautifulSoup
import time
import re
import json

def clean_input(input_str):
    cleaned_str = re.sub(r'[^a-zA-Z\s]', '', input_str)
    return cleaned_str

def select_file():
    file_path = filedialog.askopenfilename(filetypes=(("All files", "*"),))
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

def search_linkedin_profile():
    input_file_path = file_entry.get()
    email = 'dtrinhb3@gmail.com'  # Sử dụng tên người dùng mặc định
    password = 'Trinhquang2001@'  # Sử dụng mật khẩu mặc định
    linkedin_data = []

    try:
        driver = webdriver.Chrome()
        driver.get("https://www.linkedin.com")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "session_key")))
        email_field = driver.find_element(By.ID, "session_key")
        password_field = driver.find_element(By.ID, "session_password")
        login_button = driver.find_element(By.CLASS_NAME, "sign-in-form__submit-btn--full-width")

        email_field.send_keys(email)
        password_field.send_keys(password)
        login_button.click()

        WebDriverWait(driver, 10).until(EC.title_contains("LinkedIn"))

        input_workbook = load_workbook(input_file_path, read_only=True)
        input_sheet = input_workbook.active

        # Create a list to store data in JSON format
        json_data = []

        for row in input_sheet.iter_rows(min_row=2, values_only=True):
            if any(cell_value is not None and cell_value != "" for cell_value in row):
                ceo_name = row[0] if row[0] else ""
                company_name = row[1] if row[1] else ""
                keywords = row[2] if row[2] else ""

                query = f"{company_name} CEO {keywords} LinkedIn account"
                query = query.replace(" ", "%20")

                search_url = f"https://www.google.com/search?q={query}"

                driver.get(search_url)
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                page_source = driver.page_source

                soup = BeautifulSoup(page_source, "html.parser")
                search_results = soup.find_all('a', href=True)

                linkedin_links = []

                for result in search_results:
                    link = result['href']
                    if 'linkedin.com' in link and '/status/' not in link and 'translate' not in link and 'login' not in link and 'search' not in link:
                        linkedin_links.append(link)

                if linkedin_links:
                    for linkedin_link in linkedin_links:
                        driver.get(linkedin_link)
                        driver.implicitly_wait(10)

                        name_xpath = "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[1]/h1"
                        try:
                            name = driver.find_element(By.XPATH, name_xpath).text
                        except:
                            name = "N/A"
                        job_xpath = '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[2]'
                        try:
                            job = driver.find_element(By.XPATH, job_xpath).text
                        except:
                            job = "N/A"
                        connection_xpath = '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/ul/li[2]/span/span'
                        try:
                            connection = driver.find_element(By.XPATH, connection_xpath).text
                        except:
                            connection = "N/A"
                        location_xpath = '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[2]/span[1]'
                        try:
                            location = driver.find_element(By.XPATH, location_xpath).text
                        except:
                            location = "N/A"
                        print(job,connection,location,name)
                        json_data.append({
                            "CEO Name": name,
                            "Company Name": company_name,
                            "Keywords": keywords,
                            "LinkedIn Profile": linkedin_link,
                            "Job Title" : job,
                            "Location": location,
                            "Connection" :connection,
                        })
                else:
                    json_data.append({
                        "CEO Name": ceo_name,
                        "Company Name": company_name,
                        "Keywords": keywords,
                        "Job Title" : "NaN",
                        "Connection" : "NaN",
                        "Location": "NaN",
                        "LinkedIn Profile": "No LinkedIn links found.",
                    })

        # Save JSON data to a file
        json_file_path = "linkedin_data.json"
        with open(json_file_path, "w") as json_file:
            json.dump(json_data, json_file, indent=2)

        # Save JSON data to Excel
        excel_output_file_path = "output_linkedin.xlsx"
        output_workbook = Workbook()
        output_sheet = output_workbook.active
        output_sheet.append(["CEO Name", "Company Name", "Keywords", "Job Title","Connection","Location", "LinkedIn Profile"])

        for entry in json_data:
            output_sheet.append([entry["CEO Name"], entry["Company Name"], entry["Keywords"], entry["Job Title"],entry["Connection"],entry["Location"],entry["LinkedIn Profile"]])

        output_workbook.save(excel_output_file_path)
        driver.quit()

        status_label.config(text=f"Output saved to: {excel_output_file_path} and {json_file_path}")

    except Exception as e:
        error_message = f"Error: {str(e)}"
        status_label.config(text=error_message)

root = tk.Tk()
root.title("Find Social Media Accounts")

main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack()

file_frame = tk.LabelFrame(main_frame, text="Attach input file")
file_frame.pack(fill="x", padx=10, pady=10)

file_entry = tk.Entry(file_frame, width=40)
file_entry.pack(side="left", padx=10, pady=5)

file_button = tk.Button(file_frame, text="Browse", command=select_file)
file_button.pack(side="left", padx=10, pady=5)

email_frame = tk.LabelFrame(main_frame, text="LinkedIn Email")
email_frame.pack(fill="x", padx=10, pady=10)

email_entry = tk.Entry(email_frame, width=40)
email_entry.pack(side="left", padx=10, pady=5)

password_frame = tk.LabelFrame(main_frame, text="LinkedIn Password")
password_frame.pack(fill="x", padx=10, pady=10)

password_entry = tk.Entry(password_frame, width=40, show="*")
password_entry.pack(side="left", padx=10, pady=5)

status_label = tk.Label(main_frame, text="", font=("Arial", 12))
status_label.pack(pady=10)

search_button = tk.Button(main_frame, text="Find LinkedIn Profiles", command=search_linkedin_profile)
search_button.pack(pady=5)

root.mainloop()
