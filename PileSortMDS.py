"""Browser tool for creating proximity matrices from raw pile-sort data."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Pile-sort proximity matrix generator",
    page_icon="🗂️",
    layout="wide",
)


EXAMPLE_DATA = """Participant,Apple,Banana,Orange,Cat,Dog,Rabbit,Car,Bus,Bicycle
P01,1,1,1,2,2,2,3,3,3
P02,1,1,1,2,2,2,3,3,3
P03,1,1,2,3,3,3,4,4,4
P04,2,2,2,1,1,1,3,3,3
P05,1,1,1,2,2,3,4,4,4
P06,1,1,1,2,2,2,3,3,4
"""


def read_csv(uploaded_file):
    """Read a CSV, including files saved with common Windows encoding."""
    try:
        return pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding="cp1252")


def create_proximity_matrices(data):
    """Return similarity and dissimilarity matrices for complete sort data."""
    item_columns = data.columns[1:]
    item_data = data.iloc[:, 1:]
    n_participants = len(item_data)
    n_items = len(item_columns)
    similarity = np.zeros((n_items, n_items), dtype=int)

    for row in item_data.itertuples(index=False, name=None):
        values = np.asarray(row, dtype=object)
        similarity += np.equal.outer(values, values).astype(int)

    np.fill_diagonal(similarity, n_participants)
    dissimilarity = n_participants - similarity
    np.fill_diagonal(dissimilarity, 0)

    similarity_df = pd.DataFrame(
        similarity,
        index=item_columns,
        columns=item_columns,
    )
    dissimilarity_df = pd.DataFrame(
        dissimilarity,
        index=item_columns,
        columns=item_columns,
    )
    return similarity_df, dissimilarity_df


def clear_results():
    """Clear results when a different input file is selected."""
    st.session_state.pop("matrix_results", None)


st.title("Pile-sort proximity matrix generator")

st.write(
    """
    This tool converts **raw participant pile-sort data** into a similarity
    matrix and a dissimilarity matrix. It does **not** perform multidimensional
    scaling (MDS). Download a matrix from this page and conduct the MDS
    analysis separately in SPSS.
    """
)

with st.expander("Required CSV format", expanded=True):
    st.markdown(
        """
        - Each **row** represents one participant's complete sort.
        - The **first column** contains the participant or group identifier.
        - Every remaining column represents one item.
        - Within a row, items with the same pile code were placed together.
        - Pile codes may be numbers or text, but there must be no blank item
          cells.

        The actual pile numbers do not have to agree between participants.
        For example, one participant's pile `1` and another participant's
        pile `3` can represent comparable groupings. Only matches within each
        participant's row are counted.
        """
    )
    st.download_button(
        "Download example raw pile-sort CSV",
        data=EXAMPLE_DATA,
        file_name="example_raw_pile_sort_data.csv",
        mime="text/csv",
    )


uploaded_file = st.file_uploader(
    "Upload raw participant pile-sort data",
    type=["csv"],
    on_change=clear_results,
)

if uploaded_file is not None:
    try:
        data = read_csv(uploaded_file)
    except Exception as error:
        st.error(f"The CSV file could not be read: {error}")
    else:
        errors = []

        if data.empty:
            errors.append("The file contains no participant rows.")
        if data.shape[1] < 3:
            errors.append(
                "The file must contain an identifier column and at least "
                "two item columns."
            )
        if data.columns.duplicated().any():
            errors.append("Every item column must have a unique heading.")
        if data.shape[1] >= 2 and data.iloc[:, 1:].isna().any().any():
            missing_count = int(data.iloc[:, 1:].isna().sum().sum())
            errors.append(
                f"The item data contain {missing_count} blank value(s). "
                "Complete the missing pile assignments and upload the file "
                "again."
            )

        st.subheader("Uploaded data")
        st.dataframe(data, use_container_width=True, hide_index=True)

        if not errors:
            summary_col1, summary_col2 = st.columns(2)
            summary_col1.metric("Participants", len(data))
            summary_col2.metric("Items", data.shape[1] - 1)

            if st.button("Calculate proximity matrices", type="primary"):
                similarity_df, dissimilarity_df = (
                    create_proximity_matrices(data)
                )
                st.session_state["matrix_results"] = {
                    "similarity": similarity_df,
                    "dissimilarity": dissimilarity_df,
                    "source_name": Path(uploaded_file.name).stem,
                }
        else:
            for message in errors:
                st.error(message)


if "matrix_results" in st.session_state:
    results = st.session_state["matrix_results"]
    similarity_df = results["similarity"]
    dissimilarity_df = results["dissimilarity"]
    source_name = results["source_name"]

    st.success("Both proximity matrices have been calculated.")

    st.subheader("Similarity matrix")
    st.caption(
        "Larger off-diagonal values mean that the two items were placed "
        "together by more participants."
    )
    st.dataframe(similarity_df, use_container_width=True)
    st.download_button(
        "Download similarity matrix",
        data=similarity_df.to_csv(index=True, index_label=""),
        file_name=f"{source_name}_SIM_MATRIX.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.subheader("Dissimilarity matrix")
    st.caption(
        "Larger off-diagonal values mean that the two items were separated "
        "by more participants."
    )
    st.dataframe(dissimilarity_df, use_container_width=True)
    st.download_button(
        "Download dissimilarity matrix",
        data=dissimilarity_df.to_csv(index=True, index_label=""),
        file_name=f"{source_name}_DIF_MATRIX.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.info(
        "Next step: import the required matrix into SPSS and conduct the "
        "multidimensional scaling analysis there."
    )


st.divider()
st.caption("Original program by Michael Pilling. Browser version, 2026.")
