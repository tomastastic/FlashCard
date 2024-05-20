# Anki2db.py

The `Anki2db.py` file is a script that allows you to convert Anki deck files into a database format. It provides a function `convert_anki_to_db` which takes the Anki deck file as input and performs the conversion process. The script reads the Anki deck file, extracts the necessary information, and stores it in a SQLite database.

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

The `Anki2db.py` script requires the following dependencies:

- Python 3.x
- SQLite3

Please ensure that these dependencies are installed on your system before running the script.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/your/repository).

## Contact

If you have any questions or need further assistance, feel free to contact the project maintainer at [email protected]

**Note:** This README file is intentionally left blank.
