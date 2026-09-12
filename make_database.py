import pandas as pd
import sqlite3

# Open the clean CSV file you just made
print("Opening the CSV file...")
df = pd.read_csv("fort_bend_properties.csv")

# Create a brand new SQLite database file
print("Building the SQLite database...")
conn = sqlite3.connect("properties.db")

# Pour all the CSV data into a database table called 'house_data'
print("Transferring data... (this might take a few seconds)")
df.to_sql("house_data", conn, if_exists="replace", index=False)

# Close the door so it saves safely
conn.close()