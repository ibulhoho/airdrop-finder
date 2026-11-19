import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))
import html
import json
import os
import subprocess
import urllib.parse
import urllib.request
from datetime import date

DATA_FILE = "airdrops.json"
SECRET_FILE = "secret.json"
WEB_URL = "https://ibulhoho.github.io/airdrop-finder/"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_telegram_config():
    cfg = load_json(SECRET_FILE, {})
    if not cfg.get("chat_id"):
        chat_id = input("Masukkan @username_channel atau ID channel (-100...): ").strip()
        cfg["chat_id"] = chat_id
        save_json(SECRET_FILE, cfg)
    return cfg.get("bot_token"), cfg.get("chat_id")

def send_telegram(token, chat_id, item):
    text = (
        f"🔥 <b>AIRDROP BARU: {html.escape(item['name'])}</b>\n\n"
        f"📂 <b>Kategori:</b> {html.escape(item['category'])}\n"
        f"🎁 <b>Reward:</b> {html.escape(item['reward'])}\n"
        f"💰 <b>Modal:</b> {html.escape(item['cost'])}\n\n"
        f"📝 <b>Cara Garap:</b>\n{html.escape(item['steps'])}\n\n"
        f"👉 <a href=\"{html.escape(item['link'])}\">Langsung Garap di Sini</a>\n"
        f"🌐 <a href=\"{WEB_URL}\">Lihat Semua Airdrop di Web</a>"
    )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("ok"):
            print("Berhasil terkirim ke Telegram!")
        else:
            print("Gagal kirim ke Telegram:", result)

def main():
    token, chat_id = get_telegram_config()
    print("\n=== Tambah Airdrop Baru ===")
    name = input("Nama Proyek: ").strip()
    if not name:
        print("Nama proyek wajib diisi.")
        return
    category = input("Kategori (Testnet/SocialFi/Telegram/DeFi): ").strip() or "Testnet"
    reward = input("Estimasi Reward: ").strip() or "Potential Airdrop"
    cost = input("Modal (Gratis/Gas Fee): ").strip() or "Gratis"
    steps = input("Cara Garap Singkat: ").strip()
    link = input("Link Referral: ").strip()

    item = {
        "name": name,
        "category": category,
        "reward": reward,
        "cost": cost,
        "steps": steps,
        "link": link,
        "date": str(date.today())
    }

    data = load_json(DATA_FILE, [])
    data.insert(0, item)
    save_json(DATA_FILE, data)
    print(f"\nData '{name}' tersimpan di {DATA_FILE}.")

    if input("Upload ke GitHub Pages sekarang? (y/n): ").strip().lower() == "y":
        subprocess.run(["git", "add", DATA_FILE], check=True)
        subprocess.run(["git", "commit", "-m", f"Add {name}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Web ter-update!")

    if token and chat_id:
        if input("Sebar info ini ke channel Telegram? (y/n): ").strip().lower() == "y":
            send_telegram(token, chat_id, item)

if __name__ == "__main__":
    main()
