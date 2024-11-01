#!/usr/bin/env python
'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2023-08-02 21:09:10
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2023-08-02 21:09:10
Description: 
射雕DIT報告中有一欄位Resources裡有用分號隔開的多個路徑，
想找出含有COPY3的路徑，取代之後另存為input_fix.csv
'''
import sys
import pandas as pd

# Function to find and replace paths containing "Copy1"
def replace_copy1(path_list):
    for path in path_list.split(';'):
        if "COPY3" in path:
            return path
    return ""

if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python3 SD_trimCopy3Path.py your_csv.csv")
        sys.exit(1)

    # Get the input CSV file path from the command-line arguments
    input_csv_file_path = sys.argv[1]

    # Read the CSV file
    try:
        df = pd.read_csv(input_csv_file_path)
    except FileNotFoundError:
        print("Error: File not found.")
        sys.exit(1)

    # Apply the function to the 'Resource' column
    df['Resources'] = df['Resources'].apply(replace_copy1)

    # Save the updated DataFrame to a new CSV file
    output_csv_file_path = input_csv_file_path.replace(".csv", "_fixed.csv")
    df.to_csv(output_csv_file_path, index=False)    

    print("Done! The updated CSV file has been saved.")
