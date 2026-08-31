
import os
import json
from datetime import datetime
import pytz
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

prompt = """
Cari dan buatkan rekapan berita serta rumor transfer sepak bola terbaru dari jurnalis Fabrizio Romano (@FabrizioRomano) dalam 24-48 jam terakhir.

Persyaratan Output JSON:
{
  "here_we_go": [
    {"pemain": "Nama", "klub_asal": "Klub", "klub_tujuan": "Klub", "detail": "Detail singkat"}
  ],
  "update_lain": [
    {"pemain": "Nama", "klub_asal": "Klub", "klub_tujuan": "Klub", "detail": "Detail singkat"}
  ]
}
"""

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            response_mime_type="application/json"
        )
    )
    data = json.loads(response.text)
    wib = pytz.timezone('Asia/Jakarta')
    now = datetime.now(wib)
    data['tanggal'] = now.strftime('%d %B %Y')
    data['last_updated'] = now.strftime('%d %B %Y, %H:%M WIB')

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Data berhasil diperbarui!")
except Exception as e:
    print(f"Error: {e}")
