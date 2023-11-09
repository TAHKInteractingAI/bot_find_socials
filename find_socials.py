import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from openpyxl import Workbook, load_workbook
from bs4 import BeautifulSoup
import openpyxl
import tkinter as tk
from tkinter import filedialog
import re
import json
import time


def clean_input(input_str):
    # Loại bỏ các ký tự đặc biệt, chỉ giữ lại ký tự chữ cái và dấu cách
    cleaned_str = re.sub(r"[^a-zA-Z\s]", "", input_str)
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
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                page_source = driver.page_source
                driver.quit()

                soup = BeautifulSoup(page_source, "html.parser")
                search_results = soup.find_all("a", href=True)

                twitter_links = []  # List of Twitter links for each row

                for result in search_results:
                    link = result["href"]
                    if (
                        "twitter.com" in link
                        and "/status/" not in link
                        and "translate" not in link
                        and "login" not in link
                        and "search" not in link
                    ):
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

                    job_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[3]/div/div/span"
                    try:
                        job_element = driver.find_element(By.XPATH, job_xpath)
                        job = job_element.text
                    except:
                        job = "N/A"
                    followers = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[5]/div[2]/a"
                    try:
                        fl_element = driver.find_element(By.XPATH, followers)
                        follower = fl_element.text
                    except:
                        follower = "N/A"
                    location_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[4]/div/span[1]/span/span"
                    try:
                        loca_element = driver.find_element(By.XPATH, location_xpath)
                        location = loca_element.text
                    except:
                        location = "N/A"
                    # Add Twitter data to the list
                    twitter_data.append(
                        {
                            "CEO Name": ceo_name,
                            "Company Name": company_name,
                            "Keywords": keywords,
                            "Twitter Link": twitter_link,
                            "Job_title": job,
                            "Followers": follower,
                            "Location": location,
                        }
                    )

                # Close the browser when finished with this row
                driver.quit()

        # Save the Twitter data to a JSON file
        json_file_path = "output_twitter_file.json"
        with open(json_file_path, "w") as json_file:
            json.dump(twitter_data, json_file)

        # Convert the JSON data to an Excel sheet (optional)
        output_sheet.append(
            [
                "CEO Name",
                "Company Name",
                "Keywords",
                "Twitter Link",
                "Job_title",
                "Followers",
                "Location",
            ]
        )
        for entry in twitter_data:
            output_sheet.append(
                [
                    entry["CEO Name"],
                    entry["Company Name"],
                    entry["Keywords"],
                    entry["Twitter Link"],
                    entry["Job_title"],
                    entry["Followers"],
                    entry["Location"],
                ]
            )

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
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                page_source = driver.page_source
                driver.quit()

                soup = BeautifulSoup(page_source, "html.parser")
                search_results = soup.find_all(
                    "a", href=True
                )  # Find all anchor tags with href attribute

                facebook_links = []  # Danh sách các liên kết Facebook cho từng dòng

                for result in search_results:
                    link = result["href"]
                    if (
                        "facebook.com" in link
                        and "/status/" not in link
                        and "translate" not in link
                        and "login" not in link
                        and "search" not in link
                        and "help" not in link
                        and "photos" not in link
                        and "events" not in link
                        and "groups" not in link
                        and "text" not in link
                    ):
                        facebook_links.append(link)

                unique_facebook_links = list(set(facebook_links))
                driver = webdriver.Chrome()

                for facebook_link in unique_facebook_links:
                    driver.get(facebook_link)

                    driver.implicitly_wait(10)

                    name_xpath = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[1]/div/div/span/h1"
                    try:
                        name = driver.find_element(By.XPATH, name_xpath).text
                    except:
                        name = "N/A"

                    location_xpath = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[2]/div[2]/div/span"
                    try:
                        location = driver.find_element(By.XPATH, location_xpath).text
                    except:
                        location = "N/A"

                    number_xpath = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[3]/div[2]/div/div/span"
                    try:
                        number_phone = driver.find_element(By.XPATH, number_xpath).text
                    except:
                        number_phone = "N/A"
                    email_xpath = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[4]/div[2]/div/div/span"
                    try:
                        email = driver.find_element(By.XPATH, email_xpath).text
                    except:
                        email = "N/A"
                    followers_xpath = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[2]/span/a[2]"
                    try:
                        followers = driver.find_element(By.XPATH, followers_xpath).text
                    except:
                        followers = "N/A"
                    facebook_data.append(
                        {
                            "Name": name,
                            "Company Name": company_name,
                            "Keywords": keywords,
                            "Location": location,
                            "Number Phone": number_phone,
                            "Email": email,
                            "Followers": followers,
                        }
                    )
                driver.quit()
        json_file_path = "output_facebook.json"
        with open(json_file_path, "w") as json_file:
            json.dump(facebook_data, json_file)

        output_sheet.append(
            [
                "Name",
                "Company Name",
                "Keywords",
                "Location",
                "Number Phone",
                "Email",
                "Followers",
            ]
        )
        for entry in facebook_data:
            output_sheet.append(
                [
                    entry["Name"],
                    entry["Company Name"],
                    entry["Keywords"],
                    entry["Location"],
                    entry["Number Phone"],
                    entry["Email"],
                    entry["Followers"],
                ]
            )
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
    linkedin_data = []

    itere = 2
    try:
        # Export the data to a new Excel file
        input_workbook = load_workbook(input_file_path, read_only=True)
        input_sheet = input_workbook.active
        driver = webdriver.Chrome()
        driver.get("https://www.google.com")
        time.sleep(5)
        lan = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div/a[1]")
        if lan.text == "English":
            driver.get(lan.get_attribute("href"))
        # Create a list to store data in JSON format
        json_data = []
        i = 0

        for row in input_sheet.iter_rows(min_row=2, values_only=True):
            i = i + 1
            print("{}/{}".format(i, 118))
            if any(cell_value is not None and cell_value != "" for cell_value in row):
                ceo_name = row[0] if row[0] else ""
                company_name = row[1] if row[1] else ""
                keywords = row[2] if row[2] else ""

                query = f"CEO of {company_name}"
                query = query.replace(" ", "%20")
                search_url = f"https://www.google.com/search?q={query}"
                driver.get(search_url)
                time.sleep(5)
                ceo_name = ""
                try:
                    ceo_element = driver.find_element(By.CLASS_NAME, "FLP8od")
                    ceo_name = (
                        ceo_element.text if ceo_element.text != "" else "CEO Not Found"
                    )
                    print(company_name, ceo_name)
                except:
                    try:
                        ceo_element = driver.find_element(By.CLASS_NAME, "IZ6rdc")
                        ceo_name = (
                            ceo_element.text
                            if ceo_element.text != ""
                            else "CEO Not Found"
                        )
                        print(company_name, ceo_name)
                    except:
                        try:
                            ceo_element = driver.find_element(By.CLASS_NAME, "hgKElc")
                            ceoname = ceo_element.find_element(By.TAG_NAME, "b").text
                            print(company_name, ceo_name)
                        except:
                            try:
                                ceo_element = driver.find_elements(
                                    By.CSS_SELECTOR, "span.hgKElc > b"
                                )
                                ceoname = ""
                                for t in ceo_element:
                                    ceoname += t.text
                                print(company_name, ceo_name)
                            except:
                                try:
                                    ceo_element = driver.find_elements(
                                        By.XPATH,
                                        "/html/body/div[6]/div/div[10]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div/span/a/h3",
                                    ).text
                                    if any(
                                        word in ceo_element
                                        for word in company_name.split()
                                    ):
                                        ceo_name = ceo_element
                                    print(company_name, ceo_name)
                                except:
                                    ceo_name = "CEO Not Found"
                                    print(company_name, ceo_name)
                if ceo_name == "" or ceo_name == "CEO Not Found":
                    query = f"CEO of {company_name}"
                    query = query.replace(" ", "%20")
                    search_url = f"https://www.google.com/search?q={query}"
                    driver.get(search_url)
                    time.sleep(5)
                    ceo_name = ""
                    try:
                        ceo_element = driver.find_element(By.CLASS_NAME, "FLP8od")
                        ceo_name = (
                            ceo_element.text
                            if ceo_element.text != ""
                            else "CEO Not Found"
                        )
                        print(company_name, ceo_name)
                    except:
                        try:
                            ceo_element = driver.find_element(By.CLASS_NAME, "IZ6rdc")
                            ceo_name = (
                                ceo_element.text
                                if ceo_element.text != ""
                                else "CEO Not Found"
                            )
                            print(company_name, ceo_name)
                        except:
                            try:
                                ceo_element = driver.find_element(
                                    By.CLASS_NAME, "hgKElc"
                                )
                                ceoname = ceo_element.find_element(
                                    By.TAG_NAME, "b"
                                ).text
                                print(company_name, ceo_name)
                            except:
                                try:
                                    ceo_element = driver.find_elements(
                                        By.CSS_SELECTOR, "span.hgKElc > b"
                                    )
                                    ceoname = ""
                                    for t in ceo_element:
                                        ceoname += t.text
                                    print(company_name, ceo_name)
                                except:
                                    try:
                                        ceo_element = driver.find_elements(
                                            By.XPATH,
                                            "/html/body/div[6]/div/div[10]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div/span/a/h3",
                                        ).text
                                        if any(
                                            word in ceo_element
                                            for word in company_name.split()
                                        ):
                                            ceo_name = ceo_element
                                        print(company_name, ceo_name)
                                    except:
                                        ceo_name = "CEO Not Found"
                                        print(company_name, ceo_name)
                print(company_name, ceo_name)
                if ceo_name == "" or ceo_name == "CEO Not Found":
                    json_data.append(
                        {
                            "CEO Name": ceo_name,
                            "Company Name": company_name,
                            "Keywords": keywords,
                            "LinkedIn Profile": "CEO Not Found",
                        }
                    )
                else:
                    query = f"Linkedin {ceo_name} CEO of {company_name} US"
                    query = query.replace(" ", "%20")
                    search_url = f"https://www.google.com/search?q={query}"
                    driver.get(search_url)
                    time.sleep(5)
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                    linkedin_links = []
                    name_linkedin = []
                    search_results = driver.find_elements(
                        By.CSS_SELECTOR, "div.v7W49e > div"
                    )
                    time.sleep(5)

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    element_ = soup.find("div", jscontroller="SC7lYd")
                    # Extract the text or HTML of the element
                    if element_:
                        for element in element_:
                            # Or get the HTML of the element
                            html_inside_element = (
                                element.prettify()
                            )  # This retains the HTML structure
                            soup = BeautifulSoup(html_inside_element, "html.parser")
                            a_tag = soup.find("a")  # Find the <a> tag
                            if a_tag is not None:
                                link = a_tag.get("href")

                            h3_tag = soup.find("h3")  # Find the <a> tag

                            if h3_tag is not None:
                                name = h3_tag.get_text()
                                # Get the value of the href attribute
                                # link = soup.find_all("a", href=True)[0]
                                # print(len(link))
                                # name = soup.find_all("h3").text
                                # print(len(name))

                                if (
                                    "linkedin.com" in link
                                    and "/status/" not in link
                                    and "/post/" not in link
                                    and "post" not in link
                                    and "story" not in link
                                    and "news" not in link
                                    and "job" not in link
                                    and "today" not in link
                                    and "author" not in link
                                    and "pulse" not in link
                                    and "company" not in link
                                    and "text" not in link
                                    and "translate" not in link
                                    and "login" not in link
                                    and "search" not in link
                                ):
                                    print(link, name)
                                    linkedin_links.append(link)
                                    name_linkedin.append(name)
                                    break
                    print(len(linkedin_links))

                    if not linkedin_links:
                        json_data.append(
                            {
                                "CEO Name": ceo_name,
                                "Company Name": company_name,
                                "Keywords": keywords,
                                "LinkedIn Profile": "No LinkedIn links found.",
                            }
                        )
                    else:
                        check = 0
                        for linkedin_link, name_ in zip(linkedin_links, name_linkedin):
                            if any(word in name_ for word in ceo_name.split()):
                                json_data.append(
                                    {
                                        "CEO Name": name,
                                        "Company Name": company_name,
                                        "Keywords": keywords,
                                        "LinkedIn Profile": linkedin_link,
                                    }
                                )
                                check = 1
                                print(ceo_name, linkedin_link)

                                break
                        if not check:
                            print(ceo_name, "Cannot find Linkedin")
                            json_data.append(
                                {
                                    "CEO Name": ceo_name,
                                    "Company Name": company_name,
                                    "Keywords": keywords,
                                    "LinkedIn Profile": "No LinkedIn links found.",
                                }
                            )

        driver.quit()

        json_file_path = "linkedin_data{}.json".format(itere)
        with open(json_file_path, "w") as json_file:
            json.dump(json_data, json_file, indent=2)

        # Save JSON data to Excel
        excel_output_file_path = "output_linkedin{}.xlsx".format(itere)
        output_workbook = Workbook()
        output_sheet = output_workbook.active
        output_sheet.append(
            [
                "CEO Name",
                "Company Name",
                "Keywords",
                "LinkedIn Profile",
            ]
        )

        for entry in json_data:
            output_sheet.append(
                [
                    entry["CEO Name"],
                    entry["Company Name"],
                    entry["Keywords"],
                    entry["LinkedIn Profile"],
                ]
            )

        output_workbook.save(excel_output_file_path)

        status_label.config(
            text=f"Output saved to: {excel_output_file_path} and {json_file_path}"
        )

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
# create the status label
status_label = tk.Label(main_frame, text="", font=("Arial", 12))
status_label.pack(pady=10)

# create the send button
send_button = tk.Button(
    main_frame, text="Find Twitter Account", command=search_twitter_profile
)
send_button.pack(pady=5)

# create the send button
send_button = tk.Button(
    main_frame, text="Find Facebook Account", command=search_facebook_profile
)
send_button.pack(pady=5)

# create the send button
send_button = tk.Button(
    main_frame, text="Find LinkedIn Account", command=search_linkedin_profile
)
send_button.pack(pady=5)

root.mainloop()
