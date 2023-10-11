from csv import DictReader
from io import TextIOWrapper


def common_read_csv_file(file, encoding, model):
    """ Reading file .csv """
    csv_file = TextIOWrapper(
        file,
        encoding=encoding
    )
    reader = DictReader(csv_file)
    items = [
        model(**row)
        for row in reader
    ]
    return items
