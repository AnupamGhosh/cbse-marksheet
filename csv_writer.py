import csv
from typing import Dict, List

class CSVWriter:
    def __init__(self, filename: str, fieldnames: List[str]) -> None:
        self.filename = filename
        self.fieldnames = fieldnames

    def write_header(self, header: Dict[str, str]) -> None:
        with open(self.filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)

    def write_body(self, data: List[Dict[str, str]]) -> None:
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(data)


def main():
    CUR_DIR = os.path.dirname(__file__)
    csv_filepath = os.path.join(CUR_DIR, 'randomfile.csv')
    csv_writer = CSVWriter(csv_filepath, ['roll', 'name', 'eng', 'cs'])
    csv_writer.write_header({ 'roll': 'Roll No', 'name': 'Name', 'eng': 'English', 'cs': 'Computer & Science' })
    csv_writer.write_body([
        { 'roll': 234, 'name': 'Arnav Bagchi', 'cs': 78 },
        { 'roll': 235, 'name': 'Gaurav Lathi', 'eng': 98 }
    ])

import os
if __name__ == "__main__":
    main()