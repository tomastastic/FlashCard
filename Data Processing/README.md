# Anki2db.py

The `Anki2db.py` file is a script that allows you to convert Anki deck files into a database format. It provides a function `convert_anki_to_db` which takes the Anki deck file as input and performs the conversion process. The script reads the Anki deck file, extracts the necessary information, and stores it in a SQLite database. It can also clean the data and export it to MySQL format.

## Usage

To use the `Anki2db.py` script, follow these steps:

1. Ensure that you have Python installed on your system.
2. Download the `Anki2db.py` file and place it in your desired directory.
3. Open a terminal or command prompt and navigate to the directory where the `Anki2db.py` file is located.
4. Run the following command to execute the script:

   ```
   python Anki2db.py <anki_deck_file>
   ```

   Replace `<anki_deck_file>` with the path to your Anki deck file.

5. The script will convert the Anki deck file into a SQLite database and save it in the same directory as the input file.

## Example

Here's an example of how to use the `Anki2db.py` script:

```
python Anki2db.py my_deck.anki
```

This command will convert the `my_deck.anki` file into a SQLite database and save it as `my_deck.db` in the same directory.

## Dependencies

The `Anki2db.py` script requires the following dependencies, version is specified in requirements.txt:

- Python 
- SQLite3
- json
- os
- sqlite3
- tempfile
- zipfile
- csv
- sys
- pandas
- subprocess
- sqlalchemy


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.


