# csv-diff-cli

A command-line tool to compare and highlight differences between two CSV files with configurable output formats.

## Installation

```bash
pip install csv-diff-cli
```

Or install from source:

```bash
git clone https://github.com/yourusername/csv-diff-cli.git
cd csv-diff-cli
pip install .
```

## Usage

```bash
csv-diff file1.csv file2.csv
```

### Options

```
-k, --key COLUMN     Column to use as unique row identifier (default: first column)
-f, --format FORMAT  Output format: table, json, or csv (default: table)
-o, --output FILE    Write output to a file instead of stdout
--added              Show only added rows
--removed            Show only removed rows
--changed            Show only changed rows
```

### Example

```bash
# Compare two files using 'id' as the key column and output as JSON
csv-diff old_data.csv new_data.csv --key id --format json

# Save a diff report to a file
csv-diff report_jan.csv report_feb.csv -o diff_report.csv
```

### Sample Output

```
~ CHANGED  row 3  | name: "Alice" -> "Alicia"
+ ADDED    row 7  | id: 104, name: "Bob", age: 29
- REMOVED  row 9  | id: 201, name: "Carol", age: 34
```

## Requirements

- Python 3.8+

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the [MIT License](LICENSE).