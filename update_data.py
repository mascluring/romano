import os
import json
import re
from datetime import datetime
import pytz
import google.generativeai as genai

# Konfigurasi Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

prompt = """
Buatkan rekap berita dan rumor transfer sepak bola terbaru dari jurnalis Fabrizio Romano (@FabrizioRomano) dalam 24-48 jam terakhir.

Persyaratan Output:
Kembalikan HANYA teks berbentuk JSON murni tanpa pembungkus markdown seperti ```json.
Gunakan format struktur persis seperti ini:
{
  "here_we_go": [
    {
      "pemain": "Nama Pemain",
      "klub_asal": "Klub Asal",
      "klub_tujuan": "Klub Tujuan",
      "detail": "Detail singkat transfer (misal: €15M permanent. Medical tes hari ini.)"
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

# Data Cadangan jika API mengalami kendala kuota
default_fallback_data = {
  "here_we_go": [
    {
      "pemain": "Beto",
      "klub_asal": "Everton",
      "klub_tujuan": "Fiorentina",
      "detail": "€17 juta permanen. Tes medis dijadwalkan."
    },
    {
      "pemain": "Taylor Harwood-Bellis",
      "klub_asal": "Southampton",
      "klub_tujuan": "Aston Villa",
      "detail": "£25 juta + £5 juta add-ons. Kesepakatan selesai."
    }
  ],
  "update_lain": [
    {
      "pemain": "Cody Gakpo",
      "klub_asal": "Liverpool",
      "klub_tujuan": "Man City",
      "detail": "Negosiasi masih berlanjut antara kedua klub."
    },
    {
      "pemain": "Karim Benzema",
      "klub_asal": "Al Ittihad",
      "klub_tujuan": "-",
      "detail": "Saling sepakat putus kontrak."
    }
  ]
}

try:
    # Menggunakan Gemini 1.5 Flash standar yang stabil di Free Tier
    #model = genai.GenerativeModel('gemini-1.5-flash')
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)

    # Pembersihan teks output dari Gemini
    raw_text = response.text.replace('```json', '').replace('```', '').strip()
    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)

    if json_match:
        data = json.loads(json_match.group(0))
    else:
        print("Format JSON tidak ditemukan, menggunakan data cadangan.")
        data = default_fallback_data

except Exception as e:
    print(f"Error memanggil Gemini API: {e}. Menggunakan data cadangan.")
    data = default_fallback_data

# Tambahkan Timestamp WIB
wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(wib)
data['tanggal'] = now.strftime('%d %B %Y')
data['last_updated'] = now.strftime('%d %B %Y, %H:%M WIB')

# Simpan ke file data.json
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("File data.json berhasil diperbarui!")
