# Pile-sort proximity matrix tool

A browser-based tool for creating similarity and dissimilarity matrices from raw pile-sort data.

The application is intended for teaching and research use. It runs entirely through a web browser, so users do not need to install Python.

## Input format

Upload a CSV file in which:

* each row represents one participant’s sort;
* the first column contains a participant or group identifier;
* each subsequent column represents an item;
* items assigned the same value within a row were placed in the same pile;
* there are no blank item cells.

The pile numbers do not need to have the same meaning for different participants. The tool only compares pile assignments within each participant’s row.

An example input file can be downloaded from within the application.

## Output

The application produces two CSV files:

* **Similarity matrix:** each value shows how many participants placed the two items together.
* **Dissimilarity matrix:** each value shows how many participants placed the two items in different piles.

The first column of each output file is labelled `Item` and contains the item names.

## Suggested workflow

1. Upload the raw participant pile-sort data.
2. Calculate the proximity matrices.
3. Download the required similarity or dissimilarity matrix.
4. Import the matrix into SPSS.
5. Conduct the multidimensional scaling analysis in SPSS.

This application creates the proximity matrices only. It does not conduct the MDS analysis.

## Author

Original Python program written by Michael Pilling (2025).

Browser-based Streamlit version developed from the original program.
