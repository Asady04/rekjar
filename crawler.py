import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

USERNAME = "1101220353"
PASSWORD = "1101220353"

LOGIN_URL = "https://see.labs.telkomuniversity.ac.id/praktikum/index.php/home/loginprak"
START_URL = "https://see.labs.telkomuniversity.ac.id/home"
BASE_DOMAIN = "see.labs.telkomuniversity.ac.id"

session = requests.Session()

# Login payload
payload = {
    "user_nim": USERNAME,
    "user_pass": PASSWORD,
    "login_ass": "1",
    "submit": "",
}

# Buat folder untuk simpan hasil
os.makedirs("see_pages", exist_ok=True)
os.makedirs("see_pages/assets", exist_ok=True)

# 1. Login
login_response = session.post(LOGIN_URL, data=payload)

if login_response.status_code == 200 and "logout" in login_response.text.lower():
    print("✅ Login berhasil!")
else:
    print("❌ Login gagal!")
    print(f"Status: {login_response.status_code}")
    exit()

visited = set()
to_visit = [START_URL]

def download_asset(asset_url):
    try:
        parsed_url = urlparse(asset_url)
        filename = parsed_url.path.strip("/").replace("/", "_")
        ext = os.path.splitext(filename)[1]
        if ext not in [".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".ico"]:
            return None  # hanya download jenis tertentu
        full_path = os.path.join("see_pages", "assets", filename)
        if os.path.exists(full_path):
            return f"assets/{filename}"  # sudah didownload
        asset_response = session.get(asset_url, stream=True, timeout=10)
        if asset_response.status_code == 200:
            with open(full_path, "wb") as f:
                f.write(asset_response.content)
            print(f"[+asset] {asset_url}")
            return f"assets/{filename}"
    except Exception as e:
        print(f"[x] Gagal download asset {asset_url}: {e}")
    return None

# 2. Crawler
while to_visit:
    url = to_visit.pop()
    if url in visited:
        continue
    try:
        res = session.get(url)
        visited.add(url)
        if res.status_code != 200:
            print(f"[SKIP] {url} (status {res.status_code})")
            continue

        soup = BeautifulSoup(res.text, "html.parser")

        # Download dan ganti link asset
        for tag, attr in [("img", "src"), ("link", "href"), ("script", "src")]:
            for element in soup.find_all(tag):
                if element.has_attr(attr):
                    asset_url = urljoin(url, element[attr])
                    if BASE_DOMAIN in asset_url or asset_url.startswith("/"):
                        local_path = download_asset(asset_url)
                        if local_path:
                            element[attr] = local_path  # update src/href jadi lokal

        # Simpan halaman HTML
        filename = f"see_pages/{urlparse(url).path.strip('/').replace('/', '_') or 'home'}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print(f"[✅] Tersimpan: {filename}")

        # Tambahkan link internal ke daftar kunjungan
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            if BASE_DOMAIN in link and link not in visited:
                to_visit.append(link)

    except Exception as e:
        print(f"[❌] Gagal akses {url}: {e}")
