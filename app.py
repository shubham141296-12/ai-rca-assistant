import streamlit as st
import pandas as pd
import google.generativeai as genai

# -----------------------------
# CUSTOM CSS
# -----------------------------

st.markdown("""
<style>

.stApp {
    background: linear-gradient(to right, #0f172a, #1e293b);
    color: white;
}

h1, h2, h3 {
    color: #f8fafc;
}

[data-testid="stFileUploader"] {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 12px;
}

[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 10px;
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 16px;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    background-color: #1d4ed8;
    transform: scale(1.03);
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# GEMINI CONFIG
# -----------------------------

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)

# -----------------------------
# APP HEADER
# -----------------------------

st.title("AI-Powered RCA Assistant")

st.subheader(
    "Operational Issue Analyzer for DVS Reports"
)

# -----------------------------
# FILE UPLOAD
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload DVS Excel Report",
    type=["xlsx"]
)

# -----------------------------
# EXCEL FLOW
# -----------------------------

if uploaded_file is not None:

    # Read Excel
    df = pd.read_excel(uploaded_file)

    # Display Data
    st.write("### Uploaded DVS Report")
    st.dataframe(df)

    # -----------------------------
    # KPI CALCULATIONS
    # -----------------------------

    total_datasets = len(df)

    failed_validations = len(
        df[df["Validation_Status"] == "Failed"]
    )

    total_mismatch_rows = df[
        "Mismatch_Rows"
    ].sum()

    total_duplicates = (
        df["Duplicate_Rows_Source"].sum()
        +
        df["Duplicate_Rows_Target"].sum()
    )

    # -----------------------------
    # KPI DASHBOARD
    # -----------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Datasets",
        total_datasets
    )

    col2.metric(
        "Failed Validations",
        failed_validations
    )

    col3.metric(
        "Mismatch Rows",
        total_mismatch_rows
    )

    col4.metric(
        "Duplicate Rows",
        total_duplicates
    )

    # -----------------------------
    # SUMMARY BUILDING
    # -----------------------------

    summary = ""

    for index, row in df.iterrows():

        dataset = row["Dataset_Name"]

        source_count = row["Source_Count"]
        target_count = row["Target_Count"]

        missing_source = row[
            "Missing_Rows_Source"
        ]

        missing_target = row[
            "Missing_Rows_Target"
        ]

        mismatch_rows = row[
            "Mismatch_Rows"
        ]

        duplicate_source = row[
            "Duplicate_Rows_Source"
        ]

        duplicate_target = row[
            "Duplicate_Rows_Target"
        ]

        validation_status = row[
            "Validation_Status"
        ]

        summary += f"""
        Dataset: {dataset}

        Source Count: {source_count}
        Target Count: {target_count}

        Missing Rows in Source: {missing_source}
        Missing Rows in Target: {missing_target}

        Mismatch Rows: {mismatch_rows}

        Duplicate Rows in Source: {duplicate_source}
        Duplicate Rows in Target: {duplicate_target}

        Validation Status: {validation_status}

        """

    # -----------------------------
    # RCA GENERATION
    # -----------------------------

    if st.button("Generate RCA"):

        prompt = f"""
        You are an expert production support analyst for enterprise data migration systems.

        Analyze the DVS validation summary below.

        Provide concise and professional analysis.

        Response Format:

        ## Executive Summary
        Provide short overall assessment.

        ## Key Problematic Datasets
        Mention datasets with highest concern.

        ## Possible Root Causes
        - Cause 1
        - Cause 2

        ## Business Impact
        - Impact 1
        - Impact 2

        ## Priority Level
        Mention Low, Medium, or High with reason.

        ## Recommended Actions
        1. Action 1
        2. Action 2

        DVS Validation Summary:
        {summary}
        """

        with st.spinner(
            "Analyzing DVS report..."
        ):

            response = model.generate_content(
                prompt
            )

            response_text = response.text

        # Success Message
        st.success(
            "RCA Generated Successfully"
        )

        # Severity Indicator

        if "High" in response_text:

            st.error(
                "High Priority Issue Detected"
            )

        elif "Medium" in response_text:

            st.warning(
                "Medium Priority Issue Detected"
            )

        elif "Low" in response_text:

            st.success(
                "Low Priority Issue Detected"
            )

        # RCA Output

        with st.expander(
            "View RCA Analysis"
        ):

            st.markdown(response_text)

# -----------------------------
# MANUAL INPUT FALLBACK
# -----------------------------

else:

    issue = st.text_area(
        "Describe the issue manually"
    )

    if st.button("Generate RCA"):

        prompt = f"""
        You are an expert production support analyst.

        Analyze the operational issue below.

        Provide:
        - Root causes
        - Business impact
        - Recommended actions

        Issue:
        {issue}
        """

        with st.spinner(
            "Analyzing issue..."
        ):

            response = model.generate_content(
                prompt
            )

        st.success(
            "RCA Generated Successfully"
        )

        with st.expander(
            "View RCA Analysis"
        ):

            st.markdown(response.text)