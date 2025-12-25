import streamlit as st
from pathlib import Path
from downloader import download_pdfs

st.set_page_config(page_title="PDF Downloader", layout="wide")

st.title("PDF Downloader (Stable Version)")

url = st.text_input("Enter website URL")

def read_logs():
    log_file = Path("downloaded_pdfs/process.log")
    return log_file.read_text() if log_file.exists() else ""

if st.button("Download PDFs"):
    if not url:
        st.error("Enter a URL")
    else:
        with st.spinner("Downloading PDFs..."):
            count = download_pdfs(url)

        st.success(f"Downloaded {count} new PDFs")

st.subheader("Logs")
st.text_area("Process log", read_logs(), height=400)
