import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai
from google.genai import types

# 1. Obtenir credencials des dels Secrets de GitHub
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMAIL_EMISSOR = os.getenv("EMAIL_EMISSOR")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEPTOR = os.getenv("EMAIL_RECEPTOR")

client = genai.Client(api_key=GEMINI_API_KEY)
FITXER_ESTAT = "estat_estudiant.json"

def carregar_estat():
    with open(FITXER_ESTAT, "r", encoding="utf-8") as f:
        return json.load(f)

def desar_estat(estat):
    with open(FITXER_ESTAT, "w", encoding="utf-8") as f:
        json.dump(estat, f, ensure_ascii=False, indent=2)
def generar_lliço(tema_actual, nivell):
    # Sustituye la URL de abajo por el enlace de tu Google Form
    URL_FORMULARI = "https://docs.google.com/forms/d/1zfTh6i0hQEJHrjzLGy099LOYCtIFu0dbZBFjp-hj2H4/viewform"

    prompt = f"""
    Actua com un professor universitari de filosofia divulgativa.
    Genera la lliçó setmanal per al tema: "{tema_actual}".
    Nivell de l'estudiant: {nivell}.

    Escriu la resposta directament en format HTML (sense etiquetes ```html inici/final) ben estructurat amb CSS integrat per a correu electrònic.
    Inclou:
    1. Títol clar de la lliçó i introducció teòrica intuïtiva (300-400 paraules).
    2. 2 Recomanacions de lectura/articles d'accés lliure (Stanford Encyclopedia of Philosophy, Internet Encyclopedia of Philosophy, etc.).
    3. 3 Preguntes de reflexió al final per avaluar la comprensió.
    4. Al final de tot, un botó o enllaç ben visible que digui "Respondre el qüestionari d'avaluació" dirigit a aquest URL: {URL_FORMULARI}
    """
    
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
        )
    )
    return response.text


def enviar_email(assumpte, cos_html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = assumpte
    msg["From"] = EMAIL_EMISSOR
    msg["To"] = EMAIL_RECEPTOR

    msg.attach(MIMEText(cos_html, "html", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_EMISSOR, EMAIL_PASSWORD)
        server.sendmail(EMAIL_EMISSOR, EMAIL_RECEPTOR, msg.as_string())

def main():
    estat = carregar_estat()
    idx = estat.get("index_actual", 0)
    temari = estat.get("temari", [])

    if idx >= len(temari):
        print("S'ha completat tot el temari!")
        return

    tema_actual = temari[idx]
    print(f"Generant lliçó per al tema: {tema_actual}")

    cos_html = generar_lliço(tema_actual, estat.get("nivell", "Inicial"))
    enviar_email(f"🏛️ Lliçó de Filosofia Setmanal: {tema_actual}", cos_html)

    # Actualitzem l'índex per a la setmana següent
    estat["historial"].append(tema_actual)
    estat["index_actual"] = idx + 1
    desar_estat(estat)
    print("Correu enviat i estat actualitzat correctament!")

if __name__ == "__main__":
    main()
