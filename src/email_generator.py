import pandas as pd
from openai import OpenAI
from src.utils import filter_matching_customers
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def process_prospects(customers_df, prospects_df, prompt, sheet_url):
    """
    Processes the prospects DataFrame to generate email content and append matching customers.

    Parameters:
        customers_df (pd.DataFrame): A DataFrame containing customer information.
        prospects_df (pd.DataFrame): A DataFrame containing prospect information.
        prompt (str): The prompt string to be used for generating email content.
        sheet_url (str): The URL of the Google Sheet to save emails.

    Returns:
        pd.DataFrame: The prospects DataFrame with an additional column for email content.
    """
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        organization=os.getenv('ORG'),
        project=os.getenv('PROJECT')
    )

    def generate_email(prospect, matching_customers_df, prompt):
        """
        Generate an email for a prospect and append customer details.

        Parameters:
            prospect (dict): A dictionary representing a row in the prospects DataFrame.
            matching_customers_df (pd.DataFrame): A DataFrame of matching customers.
            prompt (str): The prompt string for generating the email.

        Returns:
            str: The generated email content.
        """
        # Convert the matching customers DataFrame to a string for inclusion in the email
        customer_details = matching_customers_df.to_string(index=False)

        # Modify the provided prompt to include prospect data and customer details
        full_prompt = (
            f"{prompt}\n\n"
            f"First Name: {prospect['first name']}\n"
            f"Hospital: {prospect['hospital']}\n"
            f"Title: {prospect['title']}\n"
            f"Append the following matching customer details at the end of the email:\n\n"
            f"{customer_details}"
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional email writer."},
                    {"role": "user", "content": full_prompt},
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating email: {e}"

    # Process each prospect
    email_contents = []
    for _, row in prospects_df.iterrows():
        prospect = row.to_dict()  # Convert the current row to a dictionary
        matching_customers_df = filter_matching_customers(customers_df, prospect)
        email_content = generate_email(prospect, matching_customers_df, prompt)
        email_contents.append(email_content)

    # Add the generated email content to the prospects DataFrame
    prospects_df["email content"] = email_contents

    # Save emails to Google Sheet
    save_to_google_sheet(sheet_url, prospects_df)

    return prospects_df

def save_to_google_sheet(sheet_url, prospects_df):
    """
    Saves the generated emails to a Google Sheet.

    Parameters:
        sheet_url (str): The URL of the Google Sheet.
        prospects_df (pd.DataFrame): The DataFrame containing prospect information and generated emails.
    """
    # Set up the Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('path/to/your/credentials.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open_by_url(sheet_url).sheet1

    # Clear existing content
    sheet.clear()

    # Write the DataFrame to the Google Sheet
    sheet.update([prospects_df.columns.values.tolist()] + prospects_df.values.tolist()) 