from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import pandas as pd  
import csv

from_dest = "Bengaluru"
to_dest = "New Delhi"

from_date = "29/11/2025"
return_date = "30/11/2025"

# chrome options
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# opening google flights
driver.get("https://www.google.com/travel/flights")
time.sleep(1)
print("Opened Google Flights page")

time.sleep(2)

active_element = driver.switch_to.active_element
active_element.send_keys(to_dest)
time.sleep(1)

# pressing tab twice to move to next box
actions = ActionChains(driver)
actions.send_keys(Keys.TAB).pause(0.5).send_keys(Keys.TAB).perform()
print("went to dep date field")

time.sleep(1)

# departure date
departure_date = from_date
active_element = driver.switch_to.active_element
active_element.send_keys(departure_date)
print(f"entered dep Date: {departure_date}")

time.sleep(1)

#  TAB to move to return date
actions.send_keys(Keys.TAB).perform()
print("Moved to Return date field")

time.sleep(1)

# entering return date
return_date = return_date
active_element = driver.switch_to.active_element
active_element.send_keys(return_date)
print(f"Entered Return Date: {return_date}")

time.sleep(1)

# ENTER to confirm
active_element.send_keys(Keys.ENTER)
# TAB twice to move to the next field
actions.send_keys(Keys.TAB).pause(0.5).send_keys(Keys.TAB).perform()
print("Moved to the next field")

time.sleep(1)

# ENTER on the active element
active_element = driver.switch_to.active_element
active_element.send_keys(Keys.ENTER)
print("Confirmed selection with ENTER")

print("Search initiated!")

# Going to next page ::

# ensure elements have loaded
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# scrolling multiple times to load everything
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # allowing time for content to load
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# wating for divs with aria-label to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label]')))

# extracting aria-labels of divs that start with "From"
divs = driver.find_elements(By.XPATH, '//div[@aria-label]')
filtered_labels = [div.get_attribute("aria-label") for div in divs if div.get_attribute("aria-label") and div.get_attribute("aria-label").startswith("From")]

print(filtered_labels)

structured_flights = []

for label in filtered_labels:
    try:
        # Extract price
        price = label.split("Indian rupees")[0].replace("From", "").strip() + " INR"
    except:
        price = "N/A"

    try:
        # Extract airline
        airline = label.split("flight with")[1].split(". Leaves")[0].strip()
    except:
        airline = "N/A"

    try:
        # Extract departure info
        dep_info = label.split("Leaves")[1].split("and arrives")[0].strip()
    except:
        dep_info = "N/A"

    try:
        # Extract arrival info
        arr_info = label.split("arrives at")[1].split(". Total duration")[0].strip()
    except:
        arr_info = "N/A"

    try:
        # Extract duration/time
        duration = label.split("Total duration")[1].split(". Select")[0].replace("Select flight", "").strip()
    except:
        duration = "N/A"

    structured_flights.append([dep_info, arr_info, airline, duration, price])

# Save to CSV with proper headers
with open("flight_data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Departure", "Arrival", "Airline", "Time", "Price"])
    writer.writerows(structured_flights)

print("✅ Flight data saved to flight_data.csv")

time.sleep(0) 
driver.quit()
print("Browser closed")

# flight_data is a list of structured lists
# Example: [['Bengaluru', 'Delhi', 'Air India', '10:00 AM – 12:30 PM', '₹5000'], ...]
html_table = "<table border='1' cellpadding='5' cellspacing='0'>"
html_table += "<tr><th>Departure</th><th>Arrival</th><th>Airline</th><th>Time</th><th>Price</th></tr>"

for flight in structured_flights:
    html_table += "<tr>"
    for field in flight:
        html_table += f"<td>{field}</td>"
    html_table += "</tr>"

html_table += "</table>"

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email = "jitha210806@gmail.com"
receiver_email = "jitha210806@gmail.com"
password = "fwky elmu ahex shaw"  # Gmail app password

msg = MIMEMultipart("alternative")
msg["Subject"] = "Flight Data"
msg["From"] = sender_email
msg["To"] = receiver_email

msg.attach(MIMEText(html_table, "html"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print("✅ Email sent successfully!")
