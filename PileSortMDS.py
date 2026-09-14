# Pile-sort and MDS tools

A browser-based tool for creating similarity and dissimilarity matrices from pile-sort data and viewing three-dimensional multidimensional scaling (MDS) solutions.

The application is intended for teaching and research use. It runs entirely through a web browser, so users do not need to install Python.

## Functions

### Proximity matrix calculator

The application converts pile-sort data into:

- a similarity matrix;
- a dissimilarity matrix.

The input must be a CSV file in which:

- each row represents one participant;
- the first column contains a participant or group identifier;
- each subsequent column represents an item;
- items assigned the same value were placed in the same pile.

### 3D MDS viewer

The application creates an interactive three-dimensional graph from MDS coordinates.

The input must be a CSV file in which:

- the first column contains the item labels;
- the second column contains Dimension 1;
- the third column contains Dimension 2;
- the fourth column contains Dimension 3.

The resulting graph can be rotated and enlarged, and users can inspect individual points or download the graph.

## Suggested workflow

1. Upload the original pile-sort data.
2. Download the resulting similarity or dissimilarity matrix.
3. Conduct the MDS analysis in SPSS.
4. save the SPSS coordinates as a CSV file.
5. Upload the coordinates to the 3D MDS viewer.

## Author

Original Python programs written by Michael Pilling (2024–2025).

Browser-based Streamlit version developed from the original programs.
Browser-based Streamlit version developed from the original programs.
