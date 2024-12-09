import pandas as pd
from dotenv import load_dotenv
import os
from openai import OpenAI
from src.utils import read_customer_info
from src.email_generator import process_prospects
from src.zoho_api import fetch_zoho_data
from src.automate_user_sends import automate_user_sends
from src.clean_and_load import clean_and_load
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables from .env file
load_dotenv()

def main():
    # Define the Google Sheet URLs
    prospects_sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_PROSPECTS_SHEET_ID/edit?usp=sharing"
    customers_sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_CUSTOMERS_SHEET_ID/edit?usp=sharing"
    
    # Set up the Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('path/to/your/credentials.json', scope)
    client = gspread.authorize(creds)

    # Load data from Google Sheets
    prospects_data = client.open_by_url(prospects_sheet_url).sheet1.get_all_records()
    customers_data = client.open_by_url(customers_sheet_url).sheet1.get_all_records()

    # Convert to DataFrame
    prospects_df = pd.DataFrame(prospects_data)
    customers_df = pd.DataFrame(customers_data)

    # Read the prompt from the text file
    with open("data/prompt.txt", "r") as file:
        prompt = file.read()

    # Define the Google Sheet URL for saving emails
    sheet_url = "https://docs.google.com/spreadsheets/d/143l9XA1cHDqc46PHFayx558qHNaA-m0A_oDHhUvfio/edit?usp=sharing"

    # Fetch leads from Zoho
    leads = fetch_zoho_data()

    # Process prospects to generate emails and save to Google Sheet
    result_df = process_prospects(customers_df, prospects_df, prompt, sheet_url)

    # Save the result to output folder
    output_file_name = "output/output.csv"
    result_df.to_csv(output_file_name, index=False)

    # Automate sending emails
    automate_user_sends(sheet_url, number_of_sends=20)

    # Clean and load data
    clean_and_load(sheet_url)

if __name__ == "__main__":
    main()


