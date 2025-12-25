import re
import requests
import hashlib
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text

# DOI regex
DOI_REGEX = re.compile(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', re.I)

# Simple browser UA (same behavior as your first code)
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def setup_logger(log_file):
    logger = logging.getLogger("DOWNLOADER")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fh = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def extract_doi(pdf_path):
    try:
        text = extract_text(pdf_path, maxpages=2)
        m = DOI_REGEX.search(text or "")
        return m.group(0).lower() if m else None
    except Exception:
        return None

def download_pdfs(url, out_dir="downloaded_pdfs"):
    out = Path(out_dir)
    out.mkdir(exist_ok=True)

    logger = setup_logger(out / "process.log")
    logger.info(f"START | {url}")

    # SINGLE request (important)
    response = requests.get(url, headers=HEADERS, timeout=30)
    logger.info(f"Website status: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    pdf_links = [
        requests.compat.urljoin(url, a["href"])
        for a in soup.find_all("a", href=True)
        if ".pdf" in a["href"].lower()
    ]

    logger.info(f"PDF links found: {len(pdf_links)}")

    hash_file = out / "hash.log"
    hashes = set(hash_file.read_text().splitlines()) if hash_file.exists() else set()

    downloaded = 0

    for pdf_url in pdf_links:
        try:
            r = requests.get(pdf_url, headers=HEADERS, timeout=60)
            r.raise_for_status()

            file_hash = hashlib.md5(r.content).hexdigest()
            if file_hash in hashes:
                logger.info(f"Duplicate skipped: {pdf_url}")
                continue

            temp = out / "temp.pdf"
            temp.write_bytes(r.content)

            doi = extract_doi(temp)
            name = doi.replace("/", "_") + ".pdf" if doi else "NO_DOI_" + pdf_url.split("/")[-1]

            temp.rename(out / name)
            hashes.add(file_hash)
            downloaded += 1

            logger.info(f"Saved: {name}")

        except Exception as e:
            logger.info(f"Failed: {pdf_url} | {e}")

    hash_file.write_text("\n".join(hashes))
    logger.info("END")

    return downloaded
