import os
import json
from datetime import datetime
import pytz
import google.generativeai as genai

# Konfigurasi API Key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

prompt = """
Cari dan buatkan rekapan berita serta rumor transfer sepak bola terbaru dari jurnalis Fabrizio Romano (@FabrizioRomano) dalam 24-48 jam terakhir.

Persyaratan Output:
Kembalikan HANYA JSON murni (tanpa tanda markdown ```json) dengan format persis seperti ini:
{
  "here_we_go": [
    {"pemain": "Nama Pemain", "klub_asal": "Klub Asal", "klub_tujuan": "Klub Tujuan", "detail": "Detail transfer"}
  ],
  "update_lain": [
    {"pemain": "Nama Pemain", "klub_asal": "Klub Asal", "klub_tujuan": "Klub Tujuan", "detail": "Detail transfer"}
  ]
}
"""

try:
    # Menggunakan Gemini 1.5 Flash yang mendukung pencarian otomatis
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    # Clean up output teks dari Gemini jika ada pembungkus markdown
    text_response = response.text.replace('```json', '').replace('```', '').strip()
    data = json.loads(text_response)
    
    # Tambahkan timestamp WIB
    wib = pytz.timezone('Asia/Jakarta')
    now = datetime.now(wib)
    data['tanggal'] = now.strftime('%d %B %Y')
    data['last_updated'] = now.strftime('%d %B %Y, %H:%M WIB')

    # Simpan ke file data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Data berhasil diperbarui!")

except Exception as e:
    print(f"Error: {e}")
