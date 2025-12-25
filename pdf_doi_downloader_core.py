import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from pdfminer.high_level import extract_text
import hashlib

DOI_REGEX = re.compile(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', re.I)

def extract_doi(pdf_path):
    try:
        text = extract_text(pdf_path, maxpages=2)
        match = DOI_REGEX.search(text or "")
        return match.group(0).lower() if match else None
    except Exception:
        return None

def clean_name(name):
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in name)

def download_and_rename(url, out_dir="downloaded_pdfs"):
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    hash_file = out_dir / "hash.log"
    hashes = set(hash_file.read_text().splitlines()) if hash_file.exists() else set()

    page = requests.get(url, timeout=30)
    page.raise_for_status()
    soup = BeautifulSoup(page.text, "html.parser")

    pdf_links = {
        requests.compat.urljoin(url, a["href"])
        for a in soup.find_all("a", href=True)
        if ".pdf" in a["href"].lower()
    }

    count = 0

    for pdf_url in pdf_links:
        try:
            r = requests.get(pdf_url, timeout=60)
            r.raise_for_status()

            file_hash = hashlib.md5(r.content).hexdigest()
            if file_hash in hashes:
                continue

            temp = out_dir / "temp.pdf"
            temp.write_bytes(r.content)

            doi = extract_doi(temp)
            original = clean_name(pdf_url.split("/")[-1].split("?")[0])

            if doi:
                new_name = doi.replace("/", "_") + ".pdf"
            else:
                new_name = f"NO_DOI_{original}"

            final = out_dir / new_name
            if final.exists():
                temp.unlink()
                continue

            temp.rename(final)
            hashes.add(file_hash)
            count += 1

        except Exception as e:
            print(f"Error: {pdf_url} → {e}")

    hash_file.write_text("\n".join(hashes))
    return count
