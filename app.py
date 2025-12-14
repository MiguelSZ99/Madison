from flask import Flask, render_template, request, jsonify, redirect, url_for
import random
import os
from supabase import create_client, Client

app = Flask(__name__)

# ==========================
#  SUPABASE CONFIG (Render)
# ==========================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL o SUPABASE_KEY no están configuradas")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CHAT_ID = "madison"   # puedes cambiarlo si luego quieres más chats

# ==========================
#  FRASES (sin tocar)
# ==========================
EMOCIONES = {
    "ternura": [
        "Me caes bien. Eso ya es raro.",
        "Tienes tema y eso me da más ganas de conocerte.",
        "Me gusta tu vibra.",
        "Pensé que ya no íbamos a volver a hablarnos, pero aquí estamos.",
        "Me agrada cómo fluye la conversación contigo.",
    ],
    "risa": [
        "Esto iba a ser una conversación normal y ya se desvió.",
        "Me pregunto de qué color son tus calcetines.",
        "Me pregunto qué cara pones al leer esto jaja.",
        "¿Tienes una foto de niña?",
        "Si te ríes, apenas va empezando.",
        "No soy tu entretenimiento… pero sí tu mejor distracción.",
    ],
    "picante": [
        "Yo no provoco, pero tampoco me hago el santo 😌",
        "Ya no sigas leyendo esto.",
        "No sé si esto es coqueteo… pero no lo voy a detener.",
        "Me gusta cómo va nuestra plática.",
        "Si sigues leyendo es porque te interesa 😏",
    ],
    "sorpresa": [
        "No siempre respondo rápido… hoy sí.",
        "Te estoy leyendo más de lo que crees.",
        "Curioso que sigas aquí.",
        "Me gusta tu actitud.",
        "No digo todo. Me gusta dejar algo pendiente.",
    ]
}

# ==========================
#  HELPERS SUPABASE
# ==========================
def guardar_mensaje(de, texto):
    supabase.table("mensajes").insert({
        "chat": CHAT_ID,
        "de": de,
        "texto": texto
    }).execute()

def obtener_historial():
    res = (
        supabase
        .table("mensajes")
        .select("de, texto, created_at")
        .eq("chat", CHAT_ID)
        .order("created_at", desc=False)
        .execute()
    )
    return res.data or []

# ==========================
#  ROUTES
# ==========================
@app.route("/")
def home():
    return redirect(url_for("app_view"))

@app.route("/app", methods=["GET", "POST"])
def app_view():
    frase = None

    if request.method == "POST":

        # Botones de emoción
        if "emocion" in request.form:
            emo = request.form["emocion"]
            if emo in EMOCIONES:
                frase = random.choice(EMOCIONES[emo])
                return redirect(url_for("app_view", f=frase))

        # Mensaje de ella
        if "pregunta" in request.form:
            texto = request.form["pregunta"].strip()
            if texto:
                guardar_mensaje("ella", texto)
            return redirect(url_for("app_view"))

    frase = request.args.get("f")
    return render_template(
        "index.html",
        frase_generada=frase,
        estado_url=url_for("estado")
    )

@app.route("/panel_miguel", methods=["GET"])
def panel():
    return render_template(
        "miguel.html",
        estado_url=url_for("estado"),
        post_url=url_for("post_miguel")
    )

@app.route("/post_miguel", methods=["POST"])
def post_miguel():
    texto = request.form.get("respuesta", "").strip()
    if texto:
        guardar_mensaje("miguel", texto)
    return redirect(url_for("panel"))

@app.route("/estado")
def estado():
    return jsonify({"historial": obtener_historial()})

@app.route("/favicon.ico")
def favicon():
    return ("", 204)

# ==========================
if __name__ == "__main__":
    app.run(debug=True)
