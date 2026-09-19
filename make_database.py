import pandas as pd
import sqlite3

print("Opening the CSV file...")
df = pd.read_csv("fort_bend_properties.csv")

print("Building the SQLite database...")
conn = sqlite3.connect("properties.db")

print("Transferring data... (this might take a few seconds)")
df.to_sql("house_data", conn, if_exists="replace", index=False)

conn.close()
