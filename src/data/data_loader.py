"""
Reusable functions for loading datasets.

Supported formats:
- CSV (.csv)
- Excel (.xlsx)

The loader reads the source data without automatically
removing records, changing values or handling missing data.
Those operations are handled by separate preparation functions.
"""

from pathlib import Path
from typing import Any

import pandas as pd


def load_dataset(
    file_path: str | Path,
    *,
    sheet_name: str | int = 0,
    **read_kwargs: Any
) -> pd.DataFrame:
    """
    Load a CSV or Excel dataset into a pandas DataFrame.

    Parameters
    ----------
    file_path:
        Location of the dataset to load.

    sheet_name:
        Excel worksheet name or position.
        Defaults to the first worksheet.
        This parameter is ignored for CSV files.

    **read_kwargs:
        Additional supported arguments passed to the relevant
        pandas reading function. For example, CSV files can use
        sep=";" when the columns are separated by semicolons.

    Returns
    -------
    pd.DataFrame
        The loaded dataset.

    Raises
    ------
    FileNotFoundError:
        If the supplied dataset does not exist.

    IsADirectoryError:
        If the supplied path refers to a directory.

    ValueError:
        If the file format is not supported.

    Examples
    --------
    Load a CSV file:

        data = load_dataset("data/raw/sales.csv")

    Load an Excel workbook:

        data = load_dataset("data/raw/sales.xlsx")

    Load a specific Excel worksheet:

        data = load_dataset(
            "data/raw/sales.xlsx",
            sheet_name="Sales"
        )
    """

    # Convert the supplied location into a standard Path object.
    path = Path(file_path).expanduser()

    # Check that the supplied path exists.
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset file was not found: {path}"
        )

    # Make sure the path points to a file, not a directory.
    if not path.is_file():
        raise IsADirectoryError(
            f"The supplied path is a directory, not a file: {path}"
        )

    # Identify the file format using its extension.
    file_extension = path.suffix.lower()

    # Load CSV files.
    if file_extension == ".csv":

        dataset = pd.read_csv(
            path,
            **read_kwargs
        )

    # Load modern Excel workbooks.
    elif file_extension == ".xlsx":

        dataset = pd.read_excel(
            path,
            sheet_name=sheet_name,
            **read_kwargs
        )

    # Reject file formats that have not been implemented.
    else:

        raise ValueError(
            f"Unsupported file format: {file_extension or 'no extension'}. "
            "Supported formats are .csv and .xlsx."
        )

    return dataset
