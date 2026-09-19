import pandas as pd
import sqlite3

print("Opening the CSV file...")
df = pd.read_csv("fort_bend_properties.csv")

# Creating a brand new SQLite database file
print("Building the SQLite database...")
conn = sqlite3.connect("properties.db")

# Pouring all the CSV data into a database table called 'house_data'
print("Transferring data... (this might take a few seconds)")
df.to_sql("house_data", conn, if_exists="replace", index=False)

conn.close()
