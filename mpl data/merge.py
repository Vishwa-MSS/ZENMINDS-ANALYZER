import pandas as pd

# Read CSV file
df = pd.read_csv("maharaja_2025.csv")

# Column name from which you want unique values
column_name = "bowler"

# Get unique values
unique_values = df[column_name].dropna().unique()

# Convert to DataFrame
unique_df = pd.DataFrame(unique_values, columns=[column_name])

# Save to separate CSV file
unique_df.to_csv("unique_values_output.csv", index=False)

print("Unique values extracted and saved to unique_values_output.csv")