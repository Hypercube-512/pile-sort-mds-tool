# Online pile-sort matrix calculator and 3D MDS viewer
# Based on programs written by Michael Pilling (2024-2025)

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Pile-sort and MDS tools",
    page_icon="📊",
    layout="wide",
)


def read_csv(uploaded_file):
    """Read a CSV file, including files using common Windows encoding."""
    try:
        return pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding="cp1252")


def create_proximity_matrices(data):
    """Create similarity and dissimilarity matrices from pile-sort data."""
    item_columns = data.columns[1:]
    items = data[item_columns]
    n_items = len(item_columns)
    n_participants = len(items)
    similarity_matrix = np.zeros((n_items, n_items), dtype=int)

    for row in items.itertuples(index=False, name=None):
        values = np.asarray(row, dtype=object)
        valid_values = pd.notna(values)
        same_pile = (
            np.equal.outer(values, values)
            & np.outer(valid_values, valid_values)
        )
        similarity_matrix += same_pile.astype(int)

    np.fill_diagonal(similarity_matrix, n_participants)
    dissimilarity_matrix = n_participants - similarity_matrix
    np.fill_diagonal(dissimilarity_matrix, 0)

    similarity_df = pd.DataFrame(
        similarity_matrix, columns=item_columns, index=item_columns
    )
    dissimilarity_df = pd.DataFrame(
        dissimilarity_matrix, columns=item_columns, index=item_columns
    )
    return similarity_df, dissimilarity_df


st.title("Pile-sort and MDS tools")
st.write(
    """
    Use this application to create similarity and dissimilarity matrices
    from pile-sort data and to display a three-dimensional MDS solution.
    """
)

matrix_tab, plot_tab, instructions_tab = st.tabs(
    [
        "Create proximity matrices",
        "View a 3D MDS solution",
        "Instructions",
    ]
)


with matrix_tab:
    st.header("Create proximity matrices")
    st.write(
        """
        Upload a CSV file containing the pile-sort results. Each row should
        represent one participant. The first column should contain the
        participant or group identifier. Each subsequent column should
        represent one item. Items assigned the same number were placed in
        the same pile.
        """
    )

    sorting_file = st.file_uploader(
        "Upload the pile-sort CSV file", type=["csv"], key="sorting_file"
    )

    if sorting_file is not None:
        try:
            sorting_data = read_csv(sorting_file)

            if sorting_data.empty:
                st.error("The uploaded file contains no participant rows.")
            elif sorting_data.shape[1] < 3:
                st.error(
                    "The file must contain an identifier column and at least "
                    "two item columns."
                )
            else:
                st.subheader("Data preview")
                st.dataframe(sorting_data.head(10), use_container_width=True)

                summary_col1, summary_col2 = st.columns(2)
                summary_col1.metric("Participants", len(sorting_data))
                summary_col2.metric("Items", sorting_data.shape[1] - 1)

                missing_values = int(
                    sorting_data.iloc[:, 1:].isna().sum().sum()
                )
                if missing_values:
                    st.warning(
                        f"The item data contain {missing_values} missing "
                        "value(s). Missing values will not be counted as "
                        "matching pile assignments."
                    )

                similarity_df, dissimilarity_df = (
                    create_proximity_matrices(sorting_data)
                )
                st.success("The proximity matrices have been created.")

                if st.checkbox("Show matrices on screen"):
                    st.subheader("Similarity matrix")
                    st.dataframe(similarity_df, use_container_width=True)
                    st.subheader("Dissimilarity matrix")
                    st.dataframe(dissimilarity_df, use_container_width=True)

                original_name = Path(sorting_file.name).stem
                similarity_csv = similarity_df.to_csv(
                    index=True, index_label=""
                )
                dissimilarity_csv = dissimilarity_df.to_csv(
                    index=True, index_label=""
                )

                download_col1, download_col2 = st.columns(2)
                with download_col1:
                    st.download_button(
                        "Download similarity matrix",
                        data=similarity_csv,
                        file_name=f"{original_name}_SIM_MATRIX.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
                with download_col2:
                    st.download_button(
                        "Download dissimilarity matrix",
                        data=dissimilarity_csv,
                        file_name=f"{original_name}_DIF_MATRIX.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
        except Exception as error:
            st.error(f"The file could not be processed: {error}")


with plot_tab:
    st.header("View a three-dimensional MDS solution")
    st.write(
        """
        Upload a CSV file containing the MDS coordinates. The first column
        should contain the item labels. The next three columns should contain
        the X, Y and Z coordinates.
        """
    )

    coordinate_file = st.file_uploader(
        "Upload the MDS-coordinate CSV file",
        type=["csv"],
        key="coordinate_file",
    )

    if coordinate_file is not None:
        try:
            coordinate_data = read_csv(coordinate_file)

            if coordinate_data.empty:
                st.error("The uploaded file contains no data rows.")
            elif coordinate_data.shape[1] < 4:
                st.error(
                    "The file must contain at least four columns: labels, "
                    "X coordinates, Y coordinates and Z coordinates."
                )
            else:
                labels = coordinate_data.iloc[:, 0].astype(str)
                coordinates = coordinate_data.iloc[:, 1:4].apply(
                    pd.to_numeric, errors="coerce"
                )
                invalid_rows = coordinates.isna().any(axis=1)

                if invalid_rows.any():
                    row_numbers = (
                        np.flatnonzero(invalid_rows.to_numpy()) + 2
                    ).tolist()
                    st.error(
                        "Some coordinates are missing or non-numeric. "
                        f"Please check CSV row(s): {row_numbers}"
                    )
                else:
                    x = coordinates.iloc[:, 0]
                    y = coordinates.iloc[:, 1]
                    z = coordinates.iloc[:, 2]

                    with st.expander("Graph options"):
                        graph_title = st.text_input(
                            "Graph title",
                            value="Three-dimensional MDS solution",
                        )
                        show_labels = st.checkbox(
                            "Show item labels", value=True
                        )
                        use_column_names = st.checkbox(
                            "Use the CSV column names for the axes", value=True
                        )
                        marker_size = st.slider(
                            "Point size", min_value=3, max_value=15, value=7
                        )

                    if use_column_names:
                        x_title = str(coordinate_data.columns[1])
                        y_title = str(coordinate_data.columns[2])
                        z_title = str(coordinate_data.columns[3])
                    else:
                        x_title = "X-axis"
                        y_title = "Y-axis"
                        z_title = "Z-axis"

                    plot_mode = "markers+text" if show_labels else "markers"
                    plot_labels = labels if show_labels else None

                    figure = go.Figure(
                        data=[
                            go.Scatter3d(
                                x=x,
                                y=y,
                                z=z,
                                mode=plot_mode,
                                text=plot_labels,
                                textposition="top center",
                                customdata=labels,
                                marker={
                                    "size": marker_size,
                                    "color": z,
                                    "colorscale": "RdBu",
                                    "showscale": True,
                                    "colorbar": {"title": z_title},
                                    "line": {
                                        "width": 0.5,
                                        "color": "black",
                                    },
                                    "opacity": 0.9,
                                },
                                hovertemplate=(
                                    "<b>%{customdata}</b><br>"
                                    + x_title
                                    + ": %{x:.3f}<br>"
                                    + y_title
                                    + ": %{y:.3f}<br>"
                                    + z_title
                                    + ": %{z:.3f}<extra></extra>"
                                ),
                            )
                        ]
                    )

                    figure.update_layout(
                        title=graph_title,
                        height=700,
                        margin={"l": 0, "r": 0, "b": 0, "t": 60},
                        scene={
                            "xaxis_title": x_title,
                            "yaxis_title": y_title,
                            "zaxis_title": z_title,
                            "aspectmode": "data",
                        },
                    )

                    st.plotly_chart(
                        figure,
                        use_container_width=True,
                        config={
                            "displaylogo": False,
                            "toImageButtonOptions": {
                                "format": "png",
                                "filename": "MDS_3D_plot",
                                "scale": 2,
                            },
                        },
                    )

                    st.caption(
                        "Drag to rotate the graph. Scroll to zoom. Hover over "
                        "a point to see its label and coordinates. Use the "
                        "camera button to save the graph as an image."
                    )

                    interactive_html = figure.to_html(
                        full_html=True, include_plotlyjs="cdn"
                    )
                    output_name = Path(coordinate_file.name).stem
                    st.download_button(
                        "Download interactive graph",
                        data=interactive_html,
                        file_name=f"{output_name}_3D_plot.html",
                        mime="text/html",
                    )
        except Exception as error:
            st.error(f"The file could not be processed: {error}")


with instructions_tab:
    st.header("Instructions")
    st.markdown(
        """
        ### Suggested workflow

        1. Upload the original pile-sort data under **Create proximity
           matrices**.
        2. Download the required similarity or dissimilarity matrix.
        3. Run the MDS analysis in SPSS.
        4. Save the SPSS coordinates as a CSV file.
        5. Upload the coordinate file under **View a 3D MDS solution**.
        6. Rotate, enlarge or download the resulting graph.

        ### Pile-sort input format

        - The first row contains the column headings.
        - The first column contains the participant or group identifier.
        - Every subsequent column represents one item.
        - Matching numbers indicate that items were placed in the same pile.

        ### MDS-coordinate input format

        - First column: item label.
        - Second column: Dimension 1.
        - Third column: Dimension 2.
        - Fourth column: Dimension 3.
        """
    )


st.divider()
st.caption(
    "Original programs by Michael Pilling (2024-2025). "
    "Browser-based version developed from those programs."
)
