import pandas as pd

def extract_domain(email):
    """Extract the domain from an email address."""
    return email.split('@')[-1]

def filter_matching_customers(customers_df, prospect):
    """
    Filters the customers DataFrame to find rows with email domains matching the prospect's email domain.
    
    Parameters:
        customers_df (pd.DataFrame): A DataFrame with columns ['first name', 'hospital', 'title', 'email address'].
        prospect (dict): A dictionary with keys 'first name', 'hospital', 'title', 'email address'.
    
    Returns:
        pd.DataFrame: A DataFrame with rows from customers_df that have matching email domains with the prospect.
    """
    
    # Extract the domain from the prospect's email address
    prospect_domain = extract_domain(prospect["email address"])
    
    # Extract the domains from the customers DataFrame
    customers_df["email domain"] = customers_df["email address"].apply(extract_domain)
    
    # Filter customers who have the same domain as the prospect
    matching_customers_df = customers_df[customers_df["email domain"] == prospect_domain]
    
    # Drop the temporary 'email domain' column
    matching_customers_df = matching_customers_df.drop(columns=["email domain"])
    
    return matching_customers_df


def read_customer_info(csv_file_path):
    """
    Reads customer information from a CSV file with columns: 'first name', 'hospital', and 'email'.
    
    Parameters:
        csv_file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the customer information.
    """
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file_path)
        
        # Ensure the required columns are present
        required_columns = ["first name", "title", "hospital", "email"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns in the CSV file: {', '.join(missing_columns)}")
        
        # Return the DataFrame containing the customer information
        return df
    
    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' does not exist.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


