from flask import Flask, render_template_string, request, jsonify
import nltk
import random
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
nltk.download('wordnet')

# 🧠 Load chatbot knowledge
with open('chatbot.txt', 'r', errors='ignore') as f:
    doc = f.read().lower()

sent_tokens = nltk.sent_tokenize(doc)
lemmer = nltk.stem.WordNetLemmatizer()
remove_punct_dict = dict((ord(p), None) for p in string.punctuation)

def lemtokens(tokens): return [lemmer.lemmatize(t) for t in tokens]
def lemnormalize(text): return lemtokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

def response(user_response):
    tfidfvec = TfidfVectorizer(tokenizer=lemnormalize, stop_words='english')
    tfidf = tfidfvec.fit_transform(sent_tokens + [user_response])
    vals = cosine_similarity(tfidf[-1], tfidf[:-1])
    idx = vals.argsort()[0][-1]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-1]
    if req_tfidf == 0:
        return "❓ I didn't get that. Try asking about loans, cards, or accounts."
    else:
        return sent_tokens[idx]

# 🚀 Create Flask app
app = Flask(__name__)

# 🖼️ Basic HTML with JS
html = """
<!DOCTYPE html>
<html>
<head><title>Bankie Chatbot</title></head>
<body style="font-family:Arial;padding:20px;">
  <h2>Bankie Chatbot</h2>
  <input type="text" id="userInput" placeholder="Ask me something..." style="width:300px;padding:10px;">
  <button onclick="sendMessage()">Send</button>
  <div id="chat" style="margin-top:20px;"></div>

<script>
function sendMessage() {
  const msg = document.getElementById("userInput").value;
  fetch('/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: msg})
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("chat").innerHTML += "<p><strong>You:</strong> " + msg + "</p>";
    document.getElementById("chat").innerHTML += "<p><strong>Bot:</strong> " + data.reply + "</p>";
    document.getElementById("userInput").value = "";
  });
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html)

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get("message")
    reply = response(user_msg)
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)
