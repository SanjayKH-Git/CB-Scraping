import os
import pandas as pd

folder_path = r"YP/YellowPages/Birmingham_dir"

# Get a list of all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

# Initialize an empty list to store DataFrames
dfs = []

# Iterate through each CSV file and append DataFrames to the list
for file in csv_files:
    current_data = pd.read_csv(os.path.join(folder_path, file))
    dfs.append(current_data)

# Concatenate the list of DataFrames into one DataFrame
merged_data = pd.concat(dfs, ignore_index=True)

# Remove duplicate rows based on all columns
merged_data.drop_duplicates(inplace=True)

# Save the merged data to a new CSV file
merged_data.to_csv(r"YP/YellowPages/Birmingham_dir.csv", index=False)

print("Merging complete. Merged data saved")
