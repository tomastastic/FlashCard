

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

def main():
    """Main function to run the script."""
    apkg_path = '/Users/air/Desktop/delete/WaniKani_Complete_Lv_1-60.apkg'
    db_path = extract_db_from_apkg(apkg_path)
    print_table_names(db_path, print_columns=True)
    #print_deck_names(db_path, print_fields=False)
    os.remove(db_path)

if __name__ == "__main__":
    main()
