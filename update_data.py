import os
import json
import re
from datetime import datetime
import pytz
from google import genai
from google.genai import types

# Inisialisasi Client Gemini
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

prompt = """
Cari berita dan rumor transfer sepak bola terbaru dari jurnalis Fabrizio Romano (@FabrizioRomano) dalam 24-48 jam terakhir menggunakan Google Search.

Kembalikan HANYA format JSON valid tanpa format markdown atau teks tambahan lainnya.
Format JSON harus persis seperti ini:
{
  "here_we_go": [
    {"pemain": "Nama Pemain", "klub_asal": "Klub Asal", "klub_tujuan": "Klub Tujuan", "detail": "Detail transfer singkat"}
  ],
  "update_lain": [
    {"pemain": "Nama Pemain", "klub_asal": "Klub Asal", "klub_tujuan": "Klub Tujuan", "detail": "Detail transfer singkat"}
  ]
}
"""

try:
    # Memanggil model gemini-2.5-flash dengan fitur Google Search
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )

    # Ekstraksi dan pembersihan teks agar dipastikan berupa JSON murni
    raw_text = response.text
    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    
    if json_match:
        clean_json = json_match.group(0)
        data = json.loads(clean_json)
    else:
        raise ValueError("Format JSON tidak ditemukan dalam respon AI")

    # Tambahkan Timestamp WIB
    wib = pytz.timezone('Asia/Jakarta')
    now = datetime.now(wib)
    data['tanggal'] = now.strftime('%d %B %Y')
    data['last_updated'] = now.strftime('%d %B %Y, %H:%M WIB')

    # Simpan ke data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Data berhasil diperbarui dengan Google Search!")

except Exception as e:
    print(f"Error: {e}")
