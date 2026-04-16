import json

def read_data_from_json(file_path: str) -> list:
    """
    Reads test data from a JSON array file.
    Each object becomes one test row (as a list of values).

    :param file_path: Path to the .json file
    :return:          List of rows; each row is a list of values
        """
    with open(file_path, mode="r", encoding="utf-8") as f:
        raw = json.load(f)
    data_list = [list(row.values()) for row in raw]
    return data_list
