import re
import pandas as pd
import numpy as np
import openpyxl
import streamlit as st


# Function to dynamically determine the number of organizations and process the file
def process_file(df):
    initial_columns = ['full_name', 'first_name', 'last_name',
                       'headline', 'location_name', 'summary',
                       'current_company', 'current_company_position']

    # Dynamically find the maximum organization number
    organization_columns = [col for col in df.columns if re.match(r'organization_\d+', col)]
    if not organization_columns:
        st.error("No organization columns found in the file. Please upload the correct file.")
        return None

    # Extract the maximum organization number from the column names
    num_organizations = max([int(re.search(r'\d+', col).group()) for col in organization_columns])

    # Generate organization column groups based on detected num_organizations
    org_col_groups = []
    for i in range(1, num_organizations ):
        org_cols = [f'organization_{i}', f'organization_id_{i}', f'organization_url_{i}',
                    f'organization_title_{i}', f'organization_start_{i}', f'organization_end_{i}',
                    f'organization_description_{i}', f'organization_location_{i}',
                    f'organization_website_{i}', f'organization_domain_{i}', f'position_description_{i}']
        org_col_groups.append(org_cols)

    # Create a long format dataframe by exploding organization-related columns
    df_long = pd.DataFrame()
    for group in org_col_groups:
        try:
            org_df = df[initial_columns + group].copy()
            # Ensure text columns are treated as strings for all except date fields

            # # Convert 'organization_start' and 'organization_end' from 'yyyy.mm' format to datetime
            # org_df[f'organization_start_{i}'] = pd.to_datetime(org_df[f'organization_start_{i}'], format='%Y.%m', errors='coerce')
            # org_df[f'organization_end_{i}'] = pd.to_datetime(org_df[f'organization_end_{i}'], format='%Y.%m', errors='coerce')

            org_df.columns = initial_columns + ['organization', 'organization_id', 'organization_url',
                                                'organization_title', 'organization_start', 'organization_end',
                                                'organization_description', 'organization_location',
                                                'organization_website', 'organization_domain', 'position_description']
            df_long = pd.concat([df_long, org_df], ignore_index=True)
        except KeyError as e:
            st.error(f"Column not found: {e}. Please make sure the columns match the expected format.")
            return None

    # Drop rows without organizations
    df_long = df_long.dropna(subset=['organization'])

    # Select specific columns for the final output
    new_df = df_long[['full_name', 'organization', 'organization_title', 'organization_start',
                      'organization_end', 'position_description', 'organization_location']]



    # Sort by 'full_name' and then 'organization_start'
    new_df = new_df.sort_values(by=['full_name', 'organization_start'], ascending=[True, True])

    return new_df


# Streamlit UI
st.title("Organization Data Processor")

# File upload
file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if file:
    try:
        # Determine if file is CSV or Excel and read accordingly
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # Show the first few rows of the uploaded file
        st.write("Preview of the uploaded file:")
        st.dataframe(df.head())

        # Process the file dynamically without user input for number of organizations
        processed_df = process_file(df)

        if processed_df is not None:
            # Show the first few rows of the processed data
            st.write("Preview of the processed data:")
            st.dataframe(processed_df.head())

            # Convert the processed dataframe to CSV
            csv = processed_df.to_csv(index=False).encode('utf-8')

            # Create a download button
            st.download_button(
                label="Download processed file",
                data=csv,
                file_name="processed_organizations.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
