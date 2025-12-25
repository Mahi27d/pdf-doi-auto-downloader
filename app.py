import streamlit as st
import sys
import io
import zipfile
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from downloader import download_pdfs

st.set_page_config(page_title="PDF DOI Auto Downloader", layout="wide")

DOWNLOAD_DIR = Path("downloaded_pdfs")
LOG_FILE = DOWNLOAD_DIR / "process.log"
HASH_FILE = DOWNLOAD_DIR / "hash.log"

# -------------------------
# CLEAR LOGS ON REFRESH
# -------------------------
if "initialized" not in st.session_state:
    for f in [LOG_FILE, HASH_FILE]:
        if f.exists():
            f.unlink()
    st.session_state.initialized = True
    st.session_state.ready = True

st.title("PDF DOI Auto Downloader")

url = st.text_input("Enter website URL")

def read_logs():
    return LOG_FILE.read_text() if LOG_FILE.exists() else ""

def create_zip():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for pdf in DOWNLOAD_DIR.glob("*.pdf"):
            zipf.write(pdf, pdf.name)
    buffer.seek(0)
    return buffer

def cleanup_after_download():
    for f in DOWNLOAD_DIR.glob("*"):
        if f.suffix in [".pdf", ".log"]:
            f.unlink()
    st.session_state.ready = True
    st.session_state.completed = True

# -------------------------
# MAIN ACTION
# -------------------------
if st.button("Download PDFs"):
    if not url:
        st.error("Please enter a website URL")
    else:
        st.session_state.ready = False
        st.session_state.completed = False

        with st.spinner("Scraping PDFs and extracting DOI..."):
            count = download_pdfs(url)

        if count == 0:
            st.warning("No new PDFs found.")
            st.session_state.ready = True
        else:
            st.success(f"{count} PDFs processed with DOI")

            zip_data = create_zip()

            st.download_button(
                label="⬇ Download ZIP",
                data=zip_data,
                file_name="pdfs_with_doi.zip",
                mime="application/zip",
                on_click=cleanup_after_download
            )

# -------------------------
# POST-DOWNLOAD MESSAGE
# -------------------------
if st.session_state.get("completed"):
    st.success("ZIP downloaded. System reset. Ready for next URL ✅")

# -------------------------
# LOGS
# -------------------------
st.subheader("Process Logs")
st.text_area("Logs", read_logs(), height=350)
