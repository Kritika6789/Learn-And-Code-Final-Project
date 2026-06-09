import sqlite3
import google.generativeai as genai

conn = sqlite3.connect('prm.db')
cur = conn.cursor()
cur.execute("SELECT value FROM system_configuration WHERE key='LLM_API_KEY'")
row = cur.fetchone()
api_key = row[0] if row else None
conn.close()

if api_key:
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
        print("Available models:", models)
    except Exception as e:
        print("Error listing models:", str(e))
else:
    print("No API Key found in DB.")
