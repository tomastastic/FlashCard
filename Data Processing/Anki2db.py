

'''
Goal: Find out about the structure of the file for conversion
    1. Find out the: cards, notes, decks, note types, deck options
    2. Find out what fields contain the relation keys
    3. Separate the decks into separate dbs
    4. What about sound files?
'''
import json
import os
import sqlite3
import tempfile
import zipfile
import csv
import sys  
import pandas as pd
from sqlalchemy import create_engine

# -*- coding: utf_8 -*-

def extract_db_from_apkg(apkg_path):
    """Extracts the collection.anki2 file from an .apkg file."""
    with zipfile.ZipFile(apkg_path, 'r') as myzip:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(myzip.read('collection.anki2'))
            return tmp.name

def print_table_names(db_path, print_columns=False):
    """Prints the names of all tables in a SQLite database.

    Args:
        db_path: A string representing the path to the SQLite database file.
        print_columns: A boolean indicating whether to print the columns of each table.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print("Tables in the collection.anki2 database:")
    for table in tables:
        print(table[0])
        if print_columns:
            cur.execute(f"PRAGMA table_info({table[0]});")
            columns = cur.fetchall()
            print("Columns in the {} table:".format(table[0]))
            for column in columns:
                print(f"{column[1]} ({column[2]})")  # print column name and data type
    conn.close()


def print_models(db_path, ids):
    """Prints specific rows' values from the models column in the col table.

    Args:
        db_path: A string representing the path to the SQLite database file.
        ids: A list of integers representing the id numbers of the rows.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT models FROM col;")
    all_models = cur.fetchall()
    for models in all_models:
        models_values = json.loads(models[0])
        for key, value in models_values.items():
            if int(key) in ids:
                print(f"Model ID: {key}, Model Data: {value}")
    conn.close()


def replace_char_in_db(db_path, table_name, column_name, old_char, new_char):
    """Replaces a character in a specific column of a specific table in a SQLite database.

    Args:
        db_path: A string representing the path to the SQLite database file.
        table_name: A string representing the name of the table.
        column_name: A string representing the name of the column.
        old_char: The character to be replaced.
        new_char: The character to replace with.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Update the specified column in the specified table
    cur.execute(f"""
        UPDATE {table_name}
        SET {column_name} = REPLACE({column_name}, ?, ?);
    """, (old_char, new_char))

    conn.commit()
    conn.close()


def export_table_to_csv(db_path, output_dir, table_name, columns):
    """Exports specific columns from a specific table in a SQLite database to a CSV file.

    Args:
        db_path: A string representing the path to the SQLite database file.
        output_dir: A string representing the directory to output the CSV files.
        table_name: A string representing the name of the table.
        columns: A list of strings representing the names of the columns.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create a string with the column names separated by commas
    columns_str = ', '.join(columns)

    # Get the specified columns from the specified table
    cur.execute(f"SELECT {columns_str} FROM {table_name};")
    rows = cur.fetchall()

    # Create a CSV file for the table
    with open(os.path.join(output_dir, f"{table_name}.csv"), 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter='|')  # Use pipe as delimiter
        writer.writerow(columns)
        for row in rows:
            new_row = [field.decode('utf-8-sig').replace('\x1f', '|') if isinstance(field, bytes) else field for field in row]
            writer.writerow(new_row)

    conn.close()


def printfields(db_path, id):
    """Prints a specific row's values from the flds column in the notes table.

    Args:
        db_path: A string representing the path to the SQLite database file.
        id: An integer representing the id number of the row.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f"SELECT flds FROM notes WHERE id={id};")
    flds = cur.fetchone()[0]
    print(type(flds))  # Print the type of the flds value
    flds_values = flds.split('\x1f')
    for value in flds_values:
        for char in value:
            print(hex(ord(char)))  # Print the Unicode code point of each character





def clean_csv(input_file_path, output_file_path):
    # Open the input CSV file in binary mode and read the content
    with open(input_file_path, 'rb') as file:
        binary_content = file.read()

    try:
        # Try to decode the entire content with UTF-8
        decoded_content = binary_content.decode('utf-8')
    except UnicodeDecodeError as e:
        # If there's a decoding error, find the position of the problematic character
        bad_byte_index = e.start
        # Remove the problematic character and any adjacent pipes
        cleaned_binary_content = (binary_content[:bad_byte_index].rstrip(b'|') +
                                  binary_content[bad_byte_index+1:].lstrip(b'|'))
        # Attempt to decode again
        decoded_content = cleaned_binary_content.decode('utf-8')

    # Write the cleaned content to the output CSV file
    with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
        file.write(decoded_content)





def import_csv_to_mysql(csv_file_path, mysql_db_name, table_name):
    # Create a connection to the MySQL database
    engine = create_engine(f'mysql+pymysql://root:@localhost/{mysql_db_name}')    

    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Write the data to the MySQL database
    df.to_sql(table_name, con=engine, if_exists='append', index=False)

    return f"Data imported to {mysql_db_name} database"



def main():
    """Main function to run the script."""
    apkg_path = '/Users/air/Desktop/delete/WaniKani_Complete_Lv_1-60.apkg'
    db_path = extract_db_from_apkg(apkg_path)
    print(db_path)
    #print_table_names(db_path, print_columns=True)
    ids = [1411914227416, 1413076182153, 1413061256153]
    #print_models(db_path, ids)
    #export_tables_to_csv(db_path, '/Users/air/Desktop/delete')
    #printfields(db_path,1413122652443 )

    #replace_char_in_db(db_path, 'notes', 'flds', '\x1f', '|')
    output_dir = '/Users/air/Desktop/delete/WaniKaniCSV/trimmed csv'
    table_name = 'notes'
    columns = ['flds']
    #export_table_to_csv(db_path, output_dir, table_name, columns)
    #clean_csv('/Users/air/Desktop/delete/WaniKaniCSV/trimmed csv/Import.csv', '/Users/air/Desktop/delete/WaniKaniCSV/trimmed csv/ImportClean.csv')
    import_csv_to_mysql('/Users/air/Desktop/delete/WaniKaniCSV/trimmed csv/ImportA.csv', 'Cards', 'flashcards')
    #os.remove(db_path)

if __name__ == "__main__":
    main()
