

'''
Goal: Find out about the structure of the file for conversion
    1. Find out the: cards, notes, decks, note types, deck options
    2. Find out what fields contain the relation keys
    3. Separate the decks into separate dbs
    4. What about sound files?
'''
import zipfile
import sqlite3
import os
import tempfile

# Open the .apkg file
with zipfile.ZipFile('/Users/air/Desktop/delete/WaniKani_Complete_Lv_1-60.apkg', 'r') as myzip:
    # Extract the collection.anki2 file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(myzip.read('collection.anki2'))
        temp_filename = tmp.name

# Connect to the SQLite database
conn = sqlite3.connect(temp_filename)

# Create a cursor object
cur = conn.cursor()

# Execute a query to get the names of all tables in the database
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")

# Print the names of the tables
print("Tables in the collection.anki2 database:")
print(cur.fetchall())

# Close the connection to the database
conn.close()

# Remove the temporary file
os.remove(temp_filename)
