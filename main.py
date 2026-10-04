from flask import Flask, render_template, request
import joblib
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from feature_extractor import feature
app = Flask(__name__)

model = joblib.load("model/combined_model.pkl")
vectorizer = joblib.load("model/tfidf_vectorizer.pkl")
scaler = joblib.load("model/scaler.pkl")
@app.route("/", methods=["GET", "POST"])
def home():

    result = None

    if request.method == "POST":

        url = request.form["url"]

        # Extract handcrafted features
        features = feature(url)

        # Convert to DataFrame
        feature_row = pd.DataFrame([features])

        # Make sure feature order matches training
        feature_row = feature_row[
            [
                "URL_length",
                "hyphen_count",
                "digit_count",
                "digit_ratio",
                "dot_count",
                "slash_count",
                "equals_sign_count",
                "question_sign_count",
                "has_https",
                "subdomain_count",
                "has_ip",
                "query_length",
                "path_length",
                "at_count",
                "hostname_digit_count"
            ]
        ]

        # Scale handcrafted features
        feature_scaled = scaler.transform(feature_row)

        # Convert to sparse matrix
        feature_sparse = csr_matrix(feature_scaled)

        # Generate TF-IDF features
        url_tfidf = vectorizer.transform([url])

        # Combine both
        combined = hstack([
            feature_sparse,
            url_tfidf
        ])

        prediction = model.predict(combined)[0]
        probability = model.predict_proba(combined)[0]

        if prediction == 0:
            result = {
                "label": "Likely Phishing",
                "probability": probability[0] * 100
            }
        else:
            result = {
                "label": "Likely Legitimate",
                "probability": probability[1] * 100
            }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)