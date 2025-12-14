from flask import Flask, render_template, request, jsonify, redirect, url_for
import random, os
from supabase import create_client, Client

app = Flask(__name__)

# ==========================
# SUPABASE
# ==========================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CHAT_ID = "madison"  # mismo chat siempre

# ==========================
# FRASES (NO TOCADAS)
# ==========================
EMOCIONES = {
    "ternura": [
        "Me caes bien. Eso ya es raro.",
        "Tienes tema y eso me da mas ganas de conocerte",
        "Me gusta tu vibra",
        "pense que ya no ibamos a volver a hablarnos pero aqui estamos de nuevo",
        "Me agrada cómo fluye la conversación contigo",
    ],
    "risa": [
        "Esto iba a ser una conversación normal, solo te iba a decir feliz cumpleaños y ya se desvió",
        "me pregunto de que color son tus calcetines",
        "Me pregunto que cara pones al ver esto jaja",
        "Tienes una foto de niña?",
        "Si te ríes, es el comienzo a penas",
        "No soy tu entretenimiento… pero sí puedo ser tu mejor distracción.",
        "No te estoy coqueteando… solo me estás cayendo bien sospechosamente.",
    ],
    "picante": [
        "Yo no provoco, pero si te acercas no me hare el santo 😌",
        "ya no sigas viendo esto",
        "No sé si esto es coqueteo… pero tampoco voy a detenerlo.",
        "Me gusta nuestra platica talvez luego tome otra direccion",
        "Si te tuviera de frente en un bosque oscuro y solo la luna alumbrandonos, mis 5 sentidos se activarian",
        "ya no veas esto y si lo sigues viendo es porque te intera o eres chismosa jaja",
        "No me sigas conociendo porque me voy a volver una droga",
    ],
    "sorpresa": [
        "No siempre respondo rápido… pero cuando lo hago, es porque me interesa y estoy desocupado como hoy",
        "Te estoy leyendo más de lo que crees",
        "Curioso que sigas aquí… interesante.",
        "me gusta la actitud que tienes",
        "No te voy a decir todo. Me gusta dejar algo pendiente.",
        "Si quieres saber mas de mi bienvenida si no sigamos nuestro camino"
    ]
}

# ==========================
# HELPERS SUPABASE
# ==========================
def get_historial():
    res = supabase.table("mensajes") \
        .select("de,texto,created_at") \
        .eq("chat", CHAT_ID) \
        .order("created_at", desc=False) \
        .execute()
    return res.data or []

def guardar_mensaje(de, texto):
    supabase.table("mensajes").insert({
        "chat": CHAT_ID,
        "de": de,
        "texto": texto
    }).execute()

# ==========================
# ROUTES
# ==========================
@app.route("/")
def home():
    return redirect(url_for("app_view"))

@app.route("/app", methods=["GET", "POST"])
def app_view():
    frase = None

    if request.method == "POST":
        if "emocion" in request.form:
            emo = request.form["emocion"]
            if emo in EMOCIONES:
                frase = random.choice(EMOCIONES[emo])
                return redirect(url_for("app_view", f=frase))

        if "pregunta" in request.form:
            texto = request.form["pregunta"].strip()
            if texto:
                guardar_mensaje("ella", texto)
            return redirect(url_for("app_view"))

    frase = request.args.get("f")
    return render_template("index.html", frase_generada=frase, estado_url=url_for("estado"))

@app.route("/panel_miguel")
def panel():
    return render_template("miguel.html", estado_url=url_for("estado"), post_url=url_for("post_miguel"))

@app.route("/post_miguel", methods=["POST"])
def post_miguel():
    texto = request.form.get("respuesta", "").strip()
    if texto:
        guardar_mensaje("miguel", texto)
    return redirect(url_for("panel"))

@app.route("/estado")
def estado():
    return jsonify({"historial": get_historial()})

@app.route("/favicon.ico")
def favicon():
    return ("", 204)

if __name__ == "__main__":
    app.run(debug=True)
