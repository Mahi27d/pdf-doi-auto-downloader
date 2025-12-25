import re
import requests
import hashlib
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text

# DOI pattern
DOI_REGEX = re.compile(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', re.I)

# Browser User-Agent
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def setup_logger(log_file):
    logger = logging.getLogger("PDF_DOWNLOADER")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def extract_doi(pdf_path):
    try:
        text = extract_text(pdf_path, maxpages=2)
        match = DOI_REGEX.search(text or "")
        return match.group(0).lower() if match else None
    except Exception:
        return None

def safe_name(name):
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in name)

def download_and_rename(url, output_dir="downloaded_pdfs"):
    out = Path(output_dir)
    out.mkdir(exist_ok=True)

    logger = setup_logger(out / "process.log")
    logger.info("START PROCESS")
    logger.info(f"URL: {url}")

    # Accessibility check
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        logger.info(f"Website status: {r.status_code}")

        if r.status_code in (401, 403):
            logger.error("ACCESS BLOCKED (401/403)")
            return {"error": "Access blocked (401/403)"}
    except Exception as e:
        logger.error(f"Website not reachable: {e}")
        return {"error": "Website not reachable"}

    soup = BeautifulSoup(r.text, "html.parser")

    pdf_links = {
        requests.compat.urljoin(url, a["href"])
        for a in soup.find_all("a", href=True)
        if ".pdf" in a["href"].lower()
    }

    logger.info(f"PDFs found: {len(pdf_links)}")

    hash_file = out / "hash.log"
    hashes = set(hash_file.read_text().splitlines()) if hash_file.exists() else set()

    stats = {
        "found": len(pdf_links),
        "downloaded": 0,
        "with_doi": 0,
        "no_doi": 0,
        "skipped": 0
    }

    for pdf_url in pdf_links:
        try:
            resp = requests.get(pdf_url, headers=HEADERS, timeout=60)

            if resp.status_code in (401, 403):
                logger.warning(f"Blocked PDF: {pdf_url}")
                continue

            resp.raise_for_status()

            file_hash = hashlib.md5(resp.content).hexdigest()
            if file_hash in hashes:
                stats["skipped"] += 1
                logger.info(f"Skipped duplicate: {pdf_url}")
                continue

            temp = out / "temp.pdf"
            temp.write_bytes(resp.content)

            doi = extract_doi(temp)
            original = safe_name(pdf_url.split("/")[-1].split("?")[0])

            if doi:
                filename = doi.replace("/", "_") + ".pdf"
                stats["with_doi"] += 1
                logger.info(f"DOI found: {doi}")
            else:
                filename = f"NO_DOI_{original}"
                stats["no_doi"] += 1
                logger.info("DOI not found")

            final = out / filename
            if final.exists():
                temp.unlink()
                stats["skipped"] += 1
                continue

            temp.rename(final)
            hashes.add(file_hash)
            stats["downloaded"] += 1
            logger.info(f"Saved: {filename}")

        except Exception as e:
            logger.error(f"Failed PDF: {pdf_url} | {e}")

    hash_file.write_text("\n".join(hashes))
    logger.info("END PROCESS")
    return stats
