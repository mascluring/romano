import os
import json
import re
import time
from datetime import datetime
import pytz
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

prompt = """
Cari berita dan rumor transfer sepak bola paling baru dari jurnalis Fabrizio Romano (@FabrizioRomano) di internet.

Persyaratan Output:
Kembalikan HANYA teks berbentuk JSON murni tanpa pembungkus markdown seperti ```json.
Gunakan format struktur persis seperti ini:
{
  "here_we_go": [
    {
      "pemain": "Nama Pemain",
      "klub_asal": "Klub Asal",
      "klub_tujuan": "Klub Tujuan",
      "detail": "Detail singkat transfer terkini."
    }
  ],
  "update_lain": [
    {
      "pemain": "Nama Pemain",
      "klub_asal": "Klub Asal",
      "klub_tujuan": "Klub Tujuan",
      "detail": "Penjelasan detail status rumor."
    }
  ]
}
"""

default_fallback_data = {
  "here_we_go": [],
  "update_lain": []
}

data = None
max_retries = 3

for attempt in range(max_retries):
    try:
        chat = client.chats.create(
            model='gemini-3.6-flash',
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        response = chat.send_message(prompt)
        
        raw_text = response.text
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)

        if json_match:
            data = json.loads(json_match.group(0))
            break
    except Exception as e:
        print(f"Percobaan {attempt + 1} gagal: {e}")
        if "429" in str(e) and attempt < max_retries - 1:
            print("Kena limit kuota. Menunggu 30 detik sebelum mencoba lagi...")
            time.sleep(30)
        else:
            break

if not data:
    print("Gagal mengambil data AI setelah beberapa percobaan. Menggunakan fallback.")
    data = default_fallback_data

# Tambahkan Timestamp WIB
wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(wib)
data['tanggal'] = now.strftime('%d %B %Y')
data['last_updated'] = now.strftime('%d %B %Y, %H:%M WIB')

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("File data.json berhasil diperbarui!")
