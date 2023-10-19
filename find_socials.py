import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook, load_workbook
from bs4 import BeautifulSoup
import openpyxl
import tkinter as tk
from tkinter import filedialog
import undetected_chromedriver as uc
import re
import os
import json
import time




def clean_input(input_str):
    # Loại bỏ các ký tự đặc biệt, chỉ giữ lại ký tự chữ cái và dấu cách
    cleaned_str = re.sub(r'[^a-zA-Z\s]', '', input_str)
    return cleaned_str



def select_file():
    file_path = filedialog.askopenfilename(filetypes=(("All files", "*"),))
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

def search_twitter_profile():
    try:
        # Load the input Excel file
        input_file_path = file_entry.get()

        # Open the input workbook and get the first sheet
        input_workbook = openpyxl.load_workbook(input_file_path)
        input_sheet = input_workbook.active

        # Create a new workbook for the output file
        output_workbook = openpyxl.Workbook()
        output_sheet = output_workbook.active

        # output_sheet.append(["CEO Name", "Company Name", "Keywords", "Results"])

        # Create a list to store Twitter data
        twitter_data = []

        # Loop through each row in the input sheet
        for row in input_sheet.iter_rows(min_row=2, values_only=True):
            if any(cell_value is not None and cell_value != "" for cell_value in row):
                ceo_name = row[0] if row[0] else ""
                company_name = row[1] if row[1] else ""
                keywords = row[2] if row[2] else ""

                query = f"{company_name} CEO {keywords} Twitter"
                query = query.replace(" ", "%20")

                search_url = f"https://www.google.com/search?q={query}"

                # Use regular Chrome WebDriver
                driver = webdriver.Chrome()
                driver.get(search_url)
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                page_source = driver.page_source
                driver.quit()

                soup = BeautifulSoup(page_source, "html.parser")
                search_results = soup.find_all('a', href=True) 

                twitter_links = []  # List of Twitter links for each row

                for result in search_results:
                    link = result['href']
                    if 'twitter.com' in link and '/status/' not in link and 'translate' not in link and 'login' not in link and 'search' not in link:
                        twitter_links.append(link)

                # Unique Twitter links
                unique_twitter_links = list(set(twitter_links))

                # Use a new Chrome WebDriver
                driver = webdriver.Chrome()

                # Loop through each Twitter link
                for twitter_link in unique_twitter_links:
                    # Access the Twitter link
                    driver.get(twitter_link)
                    
                    # Wait for a moment to ensure the Twitter page is fully loaded
                    driver.implicitly_wait(10)

                    # Example: Get CEO name using XPath
                    ceo_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div[1]/div/div[1]/div/div/span/span[1]"
                    try:
                        ceo_element = driver.find_element(By.XPATH, ceo_xpath)
                        ceo_name = ceo_element.text
                    except:
                        ceo_name = "N/A"

                    job_xpath ='/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[3]/div/div/span'
                    try:
                        job_element = driver.find_element(By.XPATH, job_xpath)
                        job = job_element.text
                    except:
                        job = "N/A"
                    followers='/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[5]/div[2]/a'
                    try:
                        fl_element = driver.find_element(By.XPATH,followers)
                        follower = fl_element.text
                    except:
                        follower ="N/A"
                    location_xpath = '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[4]/div/span[1]/span/span'
                    try:
                        loca_element = driver.find_element(By.XPATH,location_xpath)
                        location = loca_element.text
                    except:
                        location = "N/A"
                    # Add Twitter data to the list
                    twitter_data.append({"CEO Name": ceo_name, 
                                         "Company Name": company_name, 
                                         "Keywords": keywords, 
                                         "Twitter Link": twitter_link ,
                                         "Job_title": job ,
                                         "Followers": follower,
                                         "Location":location
                                         })

                # Close the browser when finished with this row
                driver.quit()

        # Save the Twitter data to a JSON file
        json_file_path = "output_twitter_file.json"
        with open(json_file_path, "w") as json_file:
            json.dump(twitter_data, json_file)

        # Convert the JSON data to an Excel sheet (optional)
        output_sheet.append(["CEO Name", "Company Name", "Keywords", "Twitter Link","Job_title","Followers","Location"])
        for entry in twitter_data:
            output_sheet.append([entry["CEO Name"], entry["Company Name"], entry["Keywords"], entry["Twitter Link"],entry["Job_title"],entry["Followers"],entry["Location"]])

        # Save the Excel workbook
        excel_output_file_path = "output_twitter_file.xlsx"
        output_workbook.save(excel_output_file_path)

        status_label.config(text=f"Output saved to: {excel_output_file_path}")

    except Exception as e:
        status_label.config(text="Error occurred while processing the Excel file.")


        

def search_facebook_profile():
    try:
        # Load the input Excel file
        input_file_path = file_entry.get()

        # Open the input workbook and get the first sheet
        input_workbook = openpyxl.load_workbook(input_file_path)
        input_sheet = input_workbook.active

        # Create a new workbook for the output file
        output_workbook = Workbook()
        output_sheet = output_workbook.active

        output_sheet.append(["CEO Name", "Company Name", "Keywords", "Results"])

        facebook_data = []
        # Loop through each row in the input sheet
        for row in input_sheet.iter_rows(min_row=2, values_only=True):
            if any(cell_value is not None and cell_value != "" for cell_value in row):
                ceo_name = row[0] if row[0] else ""
                company_name = row[1] if row[1] else ""
                keywords = row[2] if row[2] else ""

                query = f"{company_name} {ceo_name} {keywords} Facebook account"
                query = query.replace(" ", "%20")

                search_url = f"https://www.google.com/search?q={query}"

                driver = webdriver.Chrome()
                driver.get(search_url)
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                page_source = driver.page_source
                driver.quit()

                soup = BeautifulSoup(page_source, "html.parser")
                search_results = soup.find_all('a', href=True)  # Find all anchor tags with href attribute

                facebook_links = []  # Danh sách các liên kết Facebook cho từng dòng

                for result in search_results:
                    link = result['href']
                    if 'facebook.com' in link and '/status/' not in link and 'translate' not in link and 'login' not in link and 'search' not in link and 'help' not in link and 'photos' not in link and 'events' not in link and 'groups' not in link:
                        facebook_links.append(link)

                unique_facebook_links = list(set(facebook_links))
                driver = webdriver.Chrome()

                for facebook_link in unique_facebook_links:
                    driver.get(facebook_link)

                    driver.implicitly_wait(10)

                    name_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[1]/div/div/span/h1'
                    try:
                        name = driver.find_element(By.XPATH, name_xpath).text
                    except:
                        name = "N/A"
                    
                    location_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[2]/div[2]/div/span'
                    try:
                        location = driver.find_element(By.XPATH , location_xpath).text
                    except:
                        location = "N/A"
                    
                    number_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[3]/div[2]/div/div/span'
                    try:
                        number_phone = driver.find_element(By.XPATH , number_xpath).text
                    except:
                        number_phone = "N/A"
                    email_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[4]/div[2]/div/div/span'
                    try:
                        email = driver.find_element(By.XPATH , email_xpath).text
                    except:
                        email = "N/A"
                    followers_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[2]/span/a[2]'
                    try:
                        followers = driver.find_element(By.XPATH , followers_xpath).text
                    except:
                        followers = "N/A"
                    facebook_data.append({
                        "Name":name,
                        "Company Name": company_name,
                        "Keywords": keywords,
                        "Location":location,
                        "Number Phone" :number_phone,
                        "Email":email,
                        "Followers":followers
                    })
                driver.quit()
        json_file_path = "output_facebook.json"
        with open(json_file_path , "w") as json_file:
            json.dump(facebook_data , json_file)
        
        output_sheet.append(["Name" , "Company Name","Keywords","Location","Number Phone","Email","Followers"])
        for entry in facebook_data:
            output_sheet.append([entry["Name"] , entry["Company Name"],entry["Keywords"],entry["Location"],entry["Number Phone"],entry["Email"],entry["Followers"]])
        excel_output_file = "output_facebook.xlsx"
        output_workbook.save(excel_output_file)
        status_label.config(text=f"Output Saved")

    except Exception as e:
        status_label.config(text="Error occurred while processing the Excel file.")

                # Thêm danh sách liên kết Facebook vào dòng đầu ra
                # if facebook_links:
                #     for facebook_link in facebook_links:
                #         output_sheet.append([ceo_name, company_name, keywords, facebook_link])
                # else:
                #     # Nếu không có liên kết Facebook, thêm một dòng với thông báo "No Facebook links found."
                #     output_sheet.append([ceo_name, company_name, keywords, "No Facebook links found."])

        # Save the output workbook with the Facebook profiles for each row
    #     output_file_path = "output_facebook_file.xlsx"
    #     output_workbook.save(output_file_path)
    #     status_label.config(text=f"Output saved to: {output_file_path}")

    # except Exception as e:
    #     status_label.config(text="Error occurred while processing the Excel file.")

def search_linkedin_profile():
    input_file_path = file_entry.get()
    email = email_entry.get() 
    password = password_entry.get()
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
root.title("Find Social Media account")

# create the main frame
main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack()

# create the file frame
file_frame = tk.LabelFrame(main_frame, text="Attached input file")
file_frame.pack(fill="x", padx=10, pady=10)

file_entry = tk.Entry(file_frame, width=40)
file_entry.pack(side="left", padx=10, pady=5)

file_button = tk.Button(file_frame, text="Browser", command=select_file)
file_button.pack(side="left", padx=10, pady=5)




# ... (Previous code remains unchanged)

email_label = tk.Label(main_frame, text="Nhập account linkedin(Nếu dùng find linkedin):", font=("Arial", 12))
email_label.pack(padx=10, pady=5)

email_entry = tk.Entry(main_frame, width=40)
email_entry.pack(padx=10, pady=5)

password_label = tk.Label(main_frame, text="Nhập password linkedin(Nếu dùng find linkedin):", font=("Arial", 12))
password_label.pack(padx=10, pady=5)

password_entry = tk.Entry(main_frame, show="*", width=40)
password_entry.pack(padx=10, pady=5)

# ... (Rest of the code remains unchanged)



# create the status label
status_label = tk.Label(main_frame, text="", font=("Arial", 12))
status_label.pack(pady=10)

# create the send button
send_button = tk.Button(main_frame, text="Find Twitter Account", command=search_twitter_profile)
send_button.pack(pady=5)

# create the send button
send_button = tk.Button(main_frame, text="Find Facebook Account", command=search_facebook_profile)
send_button.pack(pady=5)

# create the send button
send_button = tk.Button(main_frame, text="Find LinkedIn Account", command=search_linkedin_profile)
send_button.pack(pady=5)

root.mainloop()
