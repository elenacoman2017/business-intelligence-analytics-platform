# ============================================================
# AUTOMATED TESTS: DATA LOADER
# ============================================================
#
# PURPOSE:
# Verify that the reusable data loader correctly handles
# supported files, invalid inputs and reading options.
#
# HOW TO RUN:
# python -m pytest tests/test_data_loader.py -v
#
# ============================================================

import pandas as pd
import pytest

from src.data.data_loader import load_dataset


# ------------------------------------------------------------
# FIXTURE 1: CREATE A REUSABLE SYNTHETIC DATASET
# ------------------------------------------------------------

@pytest.fixture
def sample_dataframe():
    # Return a small fictional business dataset.
    # Fixtures allow multiple tests to reuse the same data.

    return pd.DataFrame({
        "order_id": [1001, 1002, 1003],
        "product": ["Laptop", "Mouse", "Keyboard"],
        "quantity": [1, 2, 1],
        "unit_price": [850.00, 25.00, 45.00]
    })


# ------------------------------------------------------------
# FIXTURE 2: CREATE A TEMPORARY CSV FILE
# ------------------------------------------------------------

@pytest.fixture
def csv_file(tmp_path, sample_dataframe):
    # tmp_path is a pytest feature that creates a temporary
    # directory for test files.
    # Pytest manages this directory during test execution.

    file_path = tmp_path / "sample_sales.csv"

    sample_dataframe.to_csv(file_path, index=False)

    return file_path


# ------------------------------------------------------------
# FIXTURE 3: CREATE A TEMPORARY EXCEL WORKBOOK
# ------------------------------------------------------------

@pytest.fixture
def excel_file(tmp_path, sample_dataframe):
    # Create a workbook containing two worksheets.
    # This allows us to test both the default worksheet
    # and selecting a worksheet by name.

    file_path = tmp_path / "sample_sales.xlsx"

    with pd.ExcelWriter(file_path) as writer:
        sample_dataframe.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        sample_dataframe.to_excel(
            writer,
            sheet_name="Sales",
            index=False
        )

    return file_path


# ------------------------------------------------------------
# TEST 1: LOAD A CSV FILE
# ------------------------------------------------------------

def test_load_csv(csv_file, sample_dataframe):

    result = load_dataset(csv_file)

    pd.testing.assert_frame_equal(
        result,
        sample_dataframe
    )


# ------------------------------------------------------------
# TEST 2: LOAD THE DEFAULT EXCEL WORKSHEET
# ------------------------------------------------------------

def test_load_excel_default_sheet(excel_file, sample_dataframe):

    result = load_dataset(excel_file)

    # Excel may infer whole-number decimal values as integers.
    # Compare the data without requiring identical data types.
    pd.testing.assert_frame_equal(
        result,
        sample_dataframe,
        check_dtype=False
    )


# ------------------------------------------------------------
# TEST 3: LOAD A NAMED EXCEL WORKSHEET
# ------------------------------------------------------------

def test_load_named_excel_sheet(excel_file, sample_dataframe):

    result = load_dataset(
        excel_file,
        sheet_name="Sales"
    )

    # Excel may infer whole-number decimal values as integers.
    # Compare the data without requiring identical data types.
    pd.testing.assert_frame_equal(
        result,
        sample_dataframe,
        check_dtype=False
    )


# ------------------------------------------------------------
# TEST 4: HANDLE A MISSING FILE
# ------------------------------------------------------------

def test_missing_file_raises_error(tmp_path):

    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_dataset(missing_file)


# ------------------------------------------------------------
# TEST 5: HANDLE A DIRECTORY PATH
# ------------------------------------------------------------

def test_directory_path_raises_error(tmp_path):

    with pytest.raises(IsADirectoryError):
        load_dataset(tmp_path)


# ------------------------------------------------------------
# TEST 6: REJECT AN UNSUPPORTED FILE FORMAT
# ------------------------------------------------------------

def test_unsupported_format_raises_error(tmp_path):

    unsupported_file = tmp_path / "sample.txt"

    unsupported_file.write_text(
        "Synthetic test content.",
        encoding="utf-8"
    )

    with pytest.raises(ValueError):
        load_dataset(unsupported_file)


# ------------------------------------------------------------
# TEST 7: SUPPORT ADDITIONAL PANDAS READING ARGUMENTS
# ------------------------------------------------------------

def test_csv_separator_argument(tmp_path):

    # Create a CSV file using semicolons instead of commas.

    file_path = tmp_path / "semicolon_sales.csv"

    file_path.write_text(
        "order_id;product\n1001;Laptop\n1002;Mouse\n",
        encoding="utf-8"
    )

    result = load_dataset(
        file_path,
        sep=";"
    )

    assert list(result.columns) == [
        "order_id",
        "product"
    ]

    assert len(result) == 2
