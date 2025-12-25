import streamlit as st
from pathlib import Path
from pdf_doi_downloader_core import download_and_rename

st.set_page_config(page_title="PDF DOI Auto Downloader", layout="wide")

st.title("PDF DOI Auto Downloader")
st.caption("Logs • User-Agent • IP Blocking Checks")

url = st.text_input("Enter website URL")

def read_logs():
    log_file = Path("downloaded_pdfs/process.log")
    return log_file.read_text() if log_file.exists() else ""

if st.button("Start Download"):
    if not url:
        st.error("Please enter a URL")
    else:
        with st.spinner("Running downloader..."):
            result = download_and_rename(url)

        if "error" in result:
            st.error(result["error"])
        else:
            st.success("Completed successfully")
            st.subheader("Summary")
            st.json(result)

st.subheader("Process Logs")
st.text_area(
    "Logs",
    read_logs(),
    height=400
)
