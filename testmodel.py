from transformers import AutoModelForCausalLM, AutoTokenizer

print("🚀 Loading the model...")
model_path = "C:/Users/KIIT/Desktop/ML/startpage2/startpage/fine_tuned_tinyllama_updatedfinal"

try:
    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    print("✅ Model loaded successfully!")

    # Test query
    query = "List the most frequently asked questions in ARTIFICIAL INTELLIGENCE exams."
    inputs = tokenizer(query, return_tensors="pt")

    # Generate response
    print("🤖 Generating response...")
    outputs = model.generate(**inputs, max_length=700, temperature=0.9, top_p=0.7)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print(f"💬 Response: {response_text}")

except Exception as e:
    print(f"❌ Error loading model or generating response: {str(e)}")
