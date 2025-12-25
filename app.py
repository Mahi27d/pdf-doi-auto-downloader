import streamlit as st
import sys
from pathlib import Path

# Ensure local imports work in Streamlit Cloud / GitHub
sys.path.append(str(Path(__file__).parent))

from downloader import download_pdfs

st.set_page_config(page_title="PDF DOI Auto Downloader", layout="wide")

st.title("PDF DOI Auto Downloader (Stable)")
st.caption("Downloads PDFs and renames using DOI or NO_DOI")

url = st.text_input("Enter website URL")

def read_logs():
    log_file = Path("downloaded_pdfs/process.log")
    return log_file.read_text() if log_file.exists() else ""

if st.button("Download PDFs"):
    if not url:
        st.error("Please enter a website URL")
    else:
        with st.spinner("Downloading PDFs..."):
            count = download_pdfs(url)

        st.success(f"Downloaded {count} new PDFs")

st.subheader("Process Logs")
st.text_area(
    "Logs",
    read_logs(),
    height=400
)
