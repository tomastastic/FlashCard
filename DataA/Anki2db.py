

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
                print(column[1])
    conn.close()


def print_deck_names(db_path, print_fields=False):
    """Prints the names of all decks in a SQLite database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT decks FROM col;")
    decks = json.loads(cur.fetchone()[0])
    print("Decks in the collection.anki2 database:")
    for deck in decks.values():
        print(deck['name'])
        if print_fields:
            print(f"Fields in the {deck['name']} deck:")
            print(deck.keys())
    conn.close()

def export_tables_to_csv(db_path, output_dir):
    """Exports each table in a SQLite database to a CSV file.

    Args:
        db_path: A string representing the path to the SQLite database file.
        output_dir: A string representing the directory to output the CSV files.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get the names of all tables in the database
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()

    for table in tables:
        table_name = table[0]

        # Get all rows from the table
        cur.execute(f"SELECT * FROM {table_name};")
        rows = cur.fetchall()

        # Get the column names for the table
        cur.execute(f"PRAGMA table_info({table_name});")
        columns = [column[1] for column in cur.fetchall()]

        # Create a CSV file for the table
        with open(os.path.join(output_dir, f"{table_name}.csv"), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)

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
    flds_values = flds.split('\x1f')
    for value in flds_values:
        print(value)
    conn.close()


def main():
    """Main function to run the script."""
    apkg_path = '/Users/air/Desktop/delete/WaniKani_Complete_Lv_1-60.apkg'
    db_path = extract_db_from_apkg(apkg_path)
    print_table_names(db_path, print_columns=True)
    print_deck_names(db_path, print_fields=False)
    #export_tables_to_csv(db_path, '/Users/air/Desktop/delete')
    #printfields(db_path,1512422789857 )
    os.remove(db_path)

if __name__ == "__main__":
    main()
