import os
import json
import re
from datetime import datetime
import pytz
from google import genai
from google.genai import types

# Inisialisasi SDK Google GenAI
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Prompt dengan instruksi pencarian live hari ini
prompt = """
Cari berita dan rumor transfer sepak bola paling baru dan hangat dari jurnalis Fabrizio Romano (@FabrizioRomano) yang dilaporkan HARI INI di internet.

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

# Fallback data
default_fallback_data = {
  "here_we_go": [],
  "update_lain": []
}

try:
    # Memanggil model gemini-2.5-flash dengan Search Grounding
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )

    raw_text = response.text
    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)

    if json_match:
        data = json.loads(json_match.group(0))
    else:
        print("Format JSON tidak ditemukan, menggunakan fallback.")
        data = default_fallback_data

except Exception as e:
    print(f"Error memanggil Gemini Search API: {e}. Menggunakan fallback.")
    data = default_fallback_data

# Tambahkan Timestamp WIB
wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(wib)
data['tanggal'] = now.strftime('%d %B %Y')
data['last_updated'] = now.strftime('%d %B %Y, %H:%M WIB')

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("File data.json berhasil diperbarui dengan pencarian live!")
