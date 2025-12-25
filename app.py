import streamlit as st
from pdf_doi_downloader_core import download_and_rename
import shutil

st.set_page_config(page_title="PDF DOI Downloader")

st.title("Website PDF Downloader")
st.write("Renames PDFs using DOI or NO_DOI")

url = st.text_input("Enter website URL")

if st.button("Download PDFs"):
    if not url:
        st.error("Please enter a website URL")
    else:
        with st.spinner("Downloading PDFs..."):
            count = download_and_rename(url)

        st.success(f"Downloaded {count} PDFs")

        shutil.make_archive("downloaded_pdfs", "zip", "downloaded_pdfs")

        with open("downloaded_pdfs.zip", "rb") as f:
            st.download_button(
                "Download ZIP",
                f,
                file_name="pdfs_with_and_without_doi.zip",
                mime="application/zip"
            )
