import json
import os
import re
import sqlite3

import bcrypt
from flask import (Flask, jsonify, make_response, redirect, render_template,
                   request, session, url_for)
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)
app.secret_key = os.urandom(24)
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# ✅ Define the base model and adapter paths
base_model_path = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Ensure this is downloaded
adapter_path = r"C:\Users\KIIT\Downloads\KIIT-EDUBUDDY\KIIT-EDUBUDDY\FinalIntegratedProject\model\fine_tuned_tinyllama_updatedfinal"

# ✅ Load the base model
print("🚀 Loading the base TinyLlama model...")
model = AutoModelForCausalLM.from_pretrained(base_model_path)

# ✅ Load the LoRA adapter
print("🔄 Loading LoRA adapter...")
model = PeftModel.from_pretrained(model, adapter_path)

# ✅ Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(adapter_path)

print("✅ Model and adapter loaded successfully!")


# ✅ Serve gpt.html
@app.route("/")
def home():
    return render_template("gpt.html")

# ✅ Chat API Endpoint
@app.route("/chat", methods=["POST"])
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
        outputs = model.generate(**inputs, max_length=700,temperature=0.9, top_p=0.7)
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response_text = re.sub(r"[{}'\"]", "", response_text)
        cleaned_response = re.sub(r":\s*1,", "", response_text)
        if isinstance(response_text, list):
            formatted_response = "\n".join(cleaned_response)  # ✅ Converts list to a readable format
        else:
            formatted_response = cleaned_response.replace(". ", ".\n\n")  

        print(f"💬 Response: {formatted_response}")
        return jsonify({"response": formatted_response})

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
        
        # ✅ Send JSON success response
        return jsonify({"message": "Login successful!", "redirect": "/prj3.html"})

    return jsonify({"error": "Invalid credentials"}), 401


# ✅ Serve prj3.html Only If Logged In
@app.route("/prj3.html")
def chatbox():
    return render_template("prj3.html")


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

# ✅ Logout Route
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for('gpt'))

# ✅ Run Flask Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
