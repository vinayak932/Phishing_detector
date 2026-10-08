

```markdown
# 🛡️ Phishing URL Detector — V1

A machine learning based phishing URL detection system that analyzes URLs using handcrafted structural features and character-level TF-IDF features.

The project was built as an end-to-end ML experiment, starting from raw URL data and feature engineering, through model evaluation and error analysis, and finally integrating the trained model into a Flask web application.

> **V1 achieved 99.88% accuracy on an unseen-domain test set.**

However, this accuracy should not be interpreted as real-world phishing detection accuracy. During testing, V1 showed important generalization weaknesses on unfamiliar real-world-style URLs. These limitations became the motivation for V2.

---

## 📌 Project Overview

Phishing URLs often attempt to imitate legitimate websites while using characteristics such as:

- unusual domain structures
- excessive numbers
- suspicious subdomains
- IP addresses instead of domains
- unusual paths
- misleading URL tokens
- URL shortening
- brand impersonation

V1 investigates whether these patterns can be learned from the URL itself without visiting the website.

The system uses two complementary representations:

1. **Handcrafted URL features**
2. **Character-level TF-IDF features**

These representations are combined and passed to a Logistic Regression classifier.

### V1 Pipeline

```text
                    Raw URL
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
     Handcrafted Features   Character TF-IDF
              │                 │
              ▼                 ▼
           Scaling          TF-IDF Vectorizer
              │                 │
              └────────┬────────┘
                       ▼
                  Feature Fusion
                       │
                       ▼
              Logistic Regression
                       │
                       ▼
             Phishing / Legitimate
```

---

# 📊 Dataset

V1 uses the **LegitPhish dataset** containing labeled URLs.

After cleaning:

- **100,872 unique URLs**
- **63,492 phishing URLs**
- **37,380 legitimate URLs**
- **64,001 unique domains**

Class mapping:

```text
0 → Phishing
1 → Legitimate
```

### Class Distribution

| Class | Count | Percentage |
|---|---:|---:|
| Phishing | 63,492 | 62.94% |
| Legitimate | 37,380 | 37.06% |
| **Total** | **100,872** | **100%** |

The dataset contains many URLs belonging to repeated domains, creating a potential data leakage problem when using a normal random train/test split.

Approximately **49% of URLs belong to domains appearing more than once**.

Because of this, V1 uses a domain-aware evaluation strategy.

---

# 🔍 Data Leakage Investigation

A normal random split can place URLs from the same domain into both training and testing data.

For example:

```text
Training:
example.com/login

Testing:
example.com/account
```

The model may appear to generalize to unseen URLs while actually seeing the same domain during training.

To reduce this problem, V1 uses:

```python
StratifiedGroupKFold
```

with the domain as the grouping variable.

This creates an **unseen-domain test set**, meaning domains in the test set do not occur in the training set.

### Final Split

```text
Training URLs: 82,183
Testing URLs: 18,689

Overlapping domains: 0
```

This provides a more realistic evaluation than a simple random URL split.

---

# 🧩 Handcrafted Features

The first representation consists of structural URL features extracted directly from the raw URL.

No website is visited during feature extraction.

The final V1 trained model uses **15 handcrafted features**.

| Feature | Description |
|---|---|
| `URL_length` | Total length of the URL |
| `hyphen_count` | Number of `-` characters |
| `digit_count` | Number of numerical characters |
| `digit_ratio` | Ratio of digits to total URL length |
| `dot_count` | Number of `.` characters |
| `slash_count` | Number of `/` characters |
| `equals_sign_count` | Number of `=` characters |
| `question_sign_count` | Number of `?` characters |
| `has_https` | Whether the URL uses HTTPS |
| `subdomain_count` | Estimated number of subdomains |
| `has_ip` | Whether the hostname is an IP address |
| `query_length` | Length of the query component |
| `path_length` | Length of the URL path |
| `at_count` | Number of `@` characters |
| `hostname_digit_count` | Number of digits in the hostname |

> `path_digit_count` was explored during development but was not part of the final V1 trained model.

---

# 🔬 Feature Extraction

Python's `urllib.parse` is used to break URLs into components.

For example:

```text
https://example.com/login?id=123
```

can be separated into:

```text
scheme   → https
hostname → example.com
path     → /login
query    → id=123
```

IP addresses are detected using Python's `ipaddress` module.

This allows the model to distinguish URLs such as:

```text
https://google.com
```

from:

```text
http://192.168.1.1/login
```

---

# 📈 Exploratory Data Analysis

Several features showed strong differences between phishing and legitimate URLs.

### Average URL Length

```text
Phishing:     39.43
Legitimate:   27.55
```

### Average Digit Count

```text
Phishing:     13.48
Legitimate:    0.07
```

### Average Path Length

```text
Phishing:     13.30
Legitimate:    0.35
```

### IP Address Usage

```text
Phishing:     ~77%
Legitimate:    0%
```

These features provided strong predictive signals in the dataset.

However, these relationships are not universal rules.

Legitimate websites can contain:

- long URLs
- numerical IDs
- complex paths
- query parameters

Therefore, individual URL characteristics should not automatically be interpreted as proof of phishing.

---

# 🧠 Model 1 — Handcrafted Features

A Logistic Regression classifier was trained using the handcrafted features.

The features were standardized using `StandardScaler`.

The scaler was fitted only on the training data to prevent information leakage.

### Result

```text
Accuracy: 99.716%
```

Confusion matrix:

```text
[[11232,    46],
 [    7,  7404]]
```

Total errors:

```text
53
```

---

# 🔤 Model 2 — Character-Level TF-IDF

The raw URL itself contains useful lexical information that handcrafted features cannot capture.

For example:

```text
keraekken-loagginnusa.godaddysites.com
```

and:

```text
google.com
```

have different character patterns even if their basic structural features are similar.

V1 therefore uses character-level TF-IDF:

```python
TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 5)
)
```

The vectorizer is fitted only on the training URLs.

### Result

```text
Accuracy: 99.877%
```

Confusion matrix:

```text
[[11263,    15],
 [    8,  7403]]
```

Total errors:

```text
23
```

---

# 🧩 Model 3 — Combined Model

The strongest V1 approach combines both representations.

```text
Handcrafted Features
        +
Character TF-IDF
        ↓
Feature Fusion
        ↓
Logistic Regression
```

### Final Result

**Accuracy: 99.882%**

Confusion matrix:

```text
[[11259,    19],
 [    3,  7408]]
```

Total errors:

```text
22 / 18,689
```

### Model Comparison

| Model | Accuracy | Errors |
|---|---:|---:|
| Handcrafted Features | 99.716% | 53 |
| Character TF-IDF | 99.877% | 23 |
| **Combined Model** | **99.882%** | **22** |

The combined model was selected as the V1 model.

---

# 🔎 Error Analysis

Rather than stopping at accuracy, the 22 errors from the unseen-domain test set were manually inspected.

The model missed 19 phishing URLs and incorrectly classified 3 legitimate URLs as phishing.

Examples of missed phishing URLs include:

```text
https://ledger.peritag.com/
https://help-rogers.com/
https://tiktok-super.vip/
https://suite-trazor-en.github.io/
https://harikak-234.github.io/Netflix-Clone
https://philauberson.wixsite.com/my-swisscom-2
```

These examples revealed an important limitation.

A URL can look structurally normal while still being malicious.

For example:

```text
ledger.peritag.com
```

contains the word `ledger`, but the actual domain is:

```text
peritag.com
```

A human can recognize this as potential brand impersonation, while a purely structural URL model has limited knowledge about which domains officially belong to which brands.

---

# ⚠️ Important V1 Limitation

Although V1 achieves **99.88% accuracy on the unseen-domain test set**, additional testing showed that this number does not fully represent real-world performance.

In particular, V1 can struggle with unfamiliar URLs that differ from the training distribution.

One important example is **long legitimate URLs**.

A URL can be very long because of:

- documentation paths
- search parameters
- tracking parameters
- article IDs
- database IDs
- legitimate query strings

Therefore:

```text
Long URL ≠ Phishing
```

Similarly:

```text
HTTPS ≠ Legitimate
```

and:

```text
IP address ≠ Automatically Phishing
```

The model learns statistical patterns from its training data rather than understanding the internet in the way a human analyst does.

This limitation became the primary motivation for developing V2.

---

# 🌐 Flask Deployment

V1 was integrated into a Flask web application.

The application accepts a URL from the user and runs the same inference pipeline used during model evaluation.

```text
User
 │
 ▼
Flask Web Interface
 │
 ▼
URL Feature Extraction
 │
 ├───────────────┐
 ▼               ▼
Scaler        Character TF-IDF
 │               │
 └───────┬───────┘
         ▼
    Combined Model
         │
         ▼
    Prediction
         │
         ▼
Phishing / Legitimate
```

The prediction function returns both the predicted class and model probabilities.

---

# 💾 Saved Model Artifacts

The trained V1 system uses three main artifacts:

```text
model/
├── combined_model.pkl
├── tfidf_vectorizer.pkl
└── scaler.pkl
```

### `combined_model.pkl`

The trained Logistic Regression classifier.

### `tfidf_vectorizer.pkl`

The fitted character-level TF-IDF vectorizer.

### `scaler.pkl`

The fitted `StandardScaler` for handcrafted features.

These components must be used together because inference must reproduce the same feature representation used during training.

---

# 🏗️ Project Structure

```text
Phishing_detector/
│
├── app.py
├── feature_extractor.py
│
├── model/
│   ├── combined_model.pkl
│   ├── tfidf_vectorizer.pkl
│   └── scaler.pkl
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
└── README.md
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/vinayak932/Phishing_detector.git
cd Phishing_detector
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask application:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

# 🧪 Example Predictions

Example legitimate URL:

```text
https://google.com
```

Example phishing-style URL:

```text
http://192.168.1.1/login
```

The model returns both a predicted class and class probabilities.

These probabilities represent the model's confidence based on learned patterns. They should **not** be interpreted as guaranteed real-world probabilities.

---

# 🔐 Security & Scope

V1 performs **static URL analysis**.

It does not:

- open the URL
- download webpage content
- execute JavaScript
- inspect HTML
- inspect screenshots
- query WHOIS
- perform DNS reputation checks
- use Google Safe Browsing
- verify brand ownership

This makes the system fast and relatively safe to run, but it also limits what the model can know.

---

# 🚧 V1 → V2

V1 established a strong baseline but also exposed important weaknesses.

V2 focuses on improving **generalization**, rather than simply increasing the test-set accuracy.

V2 investigates:

- domain structure
- domain vs path vs query
- subdomain complexity
- brand/domain mismatch
- suspicious lexical patterns
- TLD information
- better real-world challenge testing
- improved feature engineering

The goal is not:

> "Make the accuracy number bigger."

The goal is:

> **Build a detector that behaves more sensibly on unfamiliar real-world URLs.**

---

# 🗺️ Roadmap

## V1 — Completed ✅

- [x] Dataset cleaning
- [x] Exploratory data analysis
- [x] URL feature engineering
- [x] Leakage investigation
- [x] Unseen-domain evaluation
- [x] Handcrafted feature model
- [x] Character TF-IDF model
- [x] Combined model
- [x] Error analysis
- [x] Model serialization
- [x] Flask integration

## V2 — In Progress 🚧

- [x] Create clean V2 notebook
- [x] Build real-world challenge set
- [x] Investigate long legitimate URLs
- [x] Separate domain/path/query analysis
- [ ] Improve domain-level features
- [ ] Investigate brand impersonation signals
- [ ] Retrain V2
- [ ] Evaluate V2 on unseen domains
- [ ] Compare V1 vs V2
- [ ] Replace Flask model with V2 artifacts

## Future Possibilities 🔮

- Domain reputation signals
- DNS-based features
- Domain age
- HTML/page-level analysis
- Screenshot-based analysis
- External reputation services
- Explainable predictions
- Better probability calibration

---

# 📚 What This Project Taught

This project is intentionally more than a classification exercise.

The main lessons from V1 were:

1. **High test accuracy does not automatically mean strong real-world generalization.**
2. **Random URL splits can hide domain leakage.**
3. **Group-aware evaluation is important for URL-based datasets.**
4. **Feature engineering requires understanding the problem, not just adding columns.**
5. **Character-level TF-IDF can capture useful URL patterns that handcrafted features miss.**
6. **Combining different representations can improve performance.**
7. **Error analysis is often more valuable than another 0.1% of accuracy.**
8. **A model can be statistically confident while still being wrong.**
9. **Deployment requires reproducing the exact training-time preprocessing pipeline.**
10. **Real-world testing can reveal weaknesses that benchmark accuracy hides.**

---

# ⚠️ Disclaimer

This project is an educational machine learning and cybersecurity project.

The predictions are probabilistic model outputs and should not be treated as definitive evidence that a URL is safe or malicious.

Do not use the system as the sole security mechanism for protecting accounts, credentials, financial information, or systems.

---

# 👨‍💻 Author

**Vinayak Dubey**

Built as an ongoing exploration of:

- Machine Learning
- Cybersecurity
- Feature Engineering
- NLP / TF-IDF
- Python
- Flask
- Model Deployment

---

## V1 Status

**V1 is complete.**

The project is now being extended into **V2**, with the main focus shifting from benchmark performance toward **better real-world generalization and domain-aware phishing detection.**
```
