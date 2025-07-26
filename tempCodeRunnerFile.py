import json
import os
import sqlite3
import bcrypt
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS, cross_origin
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)  # ✅ Fixed "__name__"
CORS(app, resources={r"/": {"origins": ""}}, supports_credentials=True)

# ✅ Correct model path
model_path = "C:/Users/KIIT/Desktop/ML/startpage2/startpage/fine_tuned_tinyllama_updatedfinal"

# ✅ Verify the path and print contents for debugging
if not os.path.exists(model_path):
    raise FileNotFoundError(f"❌ Model path not found: {model_path}")

print(f"📂 Model path exists: {model_path}")
print(f"📋 Files in model path: {os.listdir(model_path)}")

# ✅ Load the model and tokenizer
print("🚀 Loading the TinyLlama model...")
try:
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    print("✅ Model loaded successfully!")
except Exception as e:
    raise RuntimeError(f"❌ Error loading model: {str(e)}")

# ✅ Serve gpt.html
@app.route("/")
def home():
    return render_template("gpt.html")

# ✅ Chat API Endpoint
@app.route("/chat", methods=["POST"])
@cross_origin()
def chat():
    try:
        # Receive user input
        data = request.get_json()
        query = data.get("query", "").strip()
        print(f"🤔 Received query: {query}")

        if not query:
            return jsonify({"response": "Error: No input provided"}), 400

        # Generate response using TinyLlama
        inputs = tokenizer(query, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=700, temperature=0.9, top_p=0.7)
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print(f"💬 Response: {response_text}")
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"❌ Error generating response: {str(e)}")
        return jsonify({"response": f"Error: {str(e)}"}), 500

# ✅ Database Setup
DB_FILE = "database.sqlite"
if not os.path.exists(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database created successfully!")

# ✅ Registration Route
@app.route("/register", methods=["POST"])
@cross_origin()
def register():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request data"}), 400

    username, email, password = data.get("username"), data.get("email"), data.get("password")
    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_pw))
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully!"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists!"}), 400

# ✅ Login Route
@app.route("/login", methods=["POST"])
@cross_origin()
def login():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request data"}), 400

    email, password = data.get("email"), data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode("utf-8"), user[3].encode("utf-8")):
        session["user"] = {"username": user[1], "email": user[2]}
        return jsonify({"redirect": url_for("chatbox")})
    
    return jsonify({"error": "Invalid credentials"}), 401

# ✅ Serve prj3.html Only If Logged In
@app.route("/prj3.html")
@cross_origin()
def chatbox():
    if "user" not in session:
        return redirect("/")
    return render_template("prj3.html")

# ✅ Logout Route
@app.route("/logout", methods=["POST"])
@cross_origin()
def logout():
    session.clear()
    return redirect("/")

# ✅ Run Flask Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
