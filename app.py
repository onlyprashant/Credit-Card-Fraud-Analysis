# ============================================================
# Credit Card Fraud Detection Web Application
# ============================================================

from marshal import version

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
    flash,
    send_from_directory
)

import traceback
import joblib
import pandas as pd
import os

# Load demo profiles
demo_profiles = pd.read_csv("demo_profiles.csv")

from data_preprocessing import preprocess_transaction

from database import (
    initialize_database,
    register_user,
    authenticate_user,
    get_user
)

# ============================================================
# Flask App
# ============================================================

app = Flask(__name__)

app.secret_key = "credit_card_fraud_detection_2026"

initialize_database()

# ============================================================
# Load Model
# ============================================================

print("=" * 60)
print("Loading Fraud Detection Model...")
print("=" * 60)

artifacts = joblib.load("best_fraud_model.pkl")

model = artifacts["model"]

model_name = artifacts["model_name"]

feature_columns = artifacts["feature_columns"]

print(f"Model Loaded : {model_name}")

print(f"Total Features : {len(feature_columns)}")

print("=" * 60)

# ============================================================
# Home Page
# ============================================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = authenticate_user(email, password)

        if user:

            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["user_email"] = user[2]
            session["college"] = user[3]
            session["department"] = user[4]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        full_name = request.form["full_name"]

        college = request.form["college"]

        department = request.form["department"]

        email = request.form["email"]

        password = request.form["password"]

        confirm_password = request.form["confirm_password"]

        if password != confirm_password:

            flash("Passwords do not match.", "danger")

            return redirect(url_for("signup"))

        success = register_user(

            full_name,

            email,

            password,

            college,

            department

        )

        if success:

            flash("Account created successfully! Please login.", "success")

            return redirect(url_for("login"))

        flash("Email already exists.", "danger")

    return render_template("signup.html")

@app.route("/profile")
def profile():

    if "user_id" not in session:

        return redirect(url_for("login"))

    return jsonify({

        "name":session["user_name"],

        "email":session["user_email"],

        "college":session["college"],

        "department":session["department"]

    })



@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(url_for("login"))

    user = get_user(session["user_id"])

    return render_template(

        "dashboard.html",

        user=user,

        model_name=model_name

    )


# ============================================================
# Helper Functions
# ============================================================

def get_risk_level(probability):

    if probability >= 0.80:
        return "CRITICAL"

    elif probability >= 0.50:
        return "HIGH"

    elif probability >= 0.20:
        return "MEDIUM"

    else:
        return "LOW"


def get_recommendation(probability):

    if probability >= 0.80:
        return "Decline transaction and contact customer."

    elif probability >= 0.50:
        return "Hold transaction for manual verification."

    elif probability >= 0.20:
        return "Monitor transaction."

    else:
        return "Transaction appears legitimate."
    

# ============================================================
# Demo Prediction API
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # ----------------------------------------
        # Receive JSON
        # ----------------------------------------

        transaction = request.get_json()

        if transaction is None:

            return jsonify({

                "error": "No JSON data received."

            }), 400

        # ----------------------------------------
        # Get User Inputs
        # ----------------------------------------

        time_value = float(transaction.get("Time", 0))

        amount_value = float(transaction.get("Amount", 0))

        # ----------------------------------------
        # Select a Real Transaction Profile
        # ----------------------------------------

        index = int(time_value + amount_value) % len(demo_profiles)

        profile = demo_profiles.iloc[index]

        # ----------------------------------------
        # Build Complete Transaction
        # ----------------------------------------

        full_transaction = {}

        full_transaction["Time"] = time_value

        full_transaction["Amount"] = amount_value

        for i in range(1, 29):

            full_transaction[f"V{i}"] = profile[f"V{i}"]

        # ----------------------------------------
        # Preprocess
        # ----------------------------------------

        data = preprocess_transaction(full_transaction)

        data = data[feature_columns]

        # ----------------------------------------
        # Prediction
        # ----------------------------------------

        probability = float(
            model.predict_proba(data)[0][1]
        )

        prediction = int(
            model.predict(data)[0]
        )

        # ----------------------------------------
        # Labels
        # ----------------------------------------

        prediction_text = (
            "Fraud"
            if prediction == 1
            else "Legitimate"
        )

        risk = get_risk_level(probability)

        recommendation = get_recommendation(probability)

        # ----------------------------------------
        # Response
        # ----------------------------------------

        return jsonify({

            "prediction": prediction_text,

            "fraud_probability": round(
                probability * 100,
                2
            ),

            "risk_level": risk,

            "recommendation": recommendation,

            "model_used": model_name

        })

    except Exception:

        traceback.print_exc()

        return jsonify({

            "error": "Prediction failed."

        }), 500


# ============================================================
# CSV Prediction API
# ============================================================

@app.route("/predict_csv", methods=["POST"])
def predict_csv():

    try:

        if "file" not in request.files:

            return jsonify({

                "error": "No file uploaded."

            }), 400

        file = request.files["file"]

        df = pd.read_csv(file)
        print(df.columns.tolist())

        print("CSV Loaded:", len(df), "rows")

        required_columns = [

            "Time",
            "Amount"

        ]

        required_columns.extend(

            [f"V{i}" for i in range(1,29)]

        )

        missing = [

            col for col in required_columns

            if col not in df.columns

        ]

        if missing:
            print("Missing Columns:", missing)
            return jsonify({

                "error":

                f"Missing columns: {missing}"

            }),400

        # Save original for display
        display_df = df.copy()

        # Preprocess

        df = preprocess_transaction(df.to_dict("records"))

        df = df[feature_columns]

        probabilities = model.predict_proba(df)[:, 1]

        predictions = model.predict(df)

        display_df["Prediction"] = [

            "Fraud" if x == 1 else "Legitimate"

            for x in predictions

        ]

        display_df["Fraud Probability"] = (

            probabilities * 100

        ).round(2)

        global latest_results

        latest_results = display_df.copy()

        fraud_count = int(predictions.sum())

        legit_count = len(predictions) - fraud_count

        print("Predictions Complete:", len(predictions), "rows")

        return jsonify({

            "total_transactions": len(predictions),

            "fraud_detected": fraud_count,

            "legitimate": legit_count,

            "results": display_df.head(100).to_dict(
                orient="records"
            ),

            "displayed rows":( min(100, len(predictions)) )

        })

    except Exception:

        traceback.print_exc()

        return jsonify({

            "error": "CSV prediction failed."

        }), 500
    

# ============================================================
# Global Storage for Latest CSV Results
# ============================================================

latest_results = None


# ============================================================
# Download CSV Results
# ============================================================

@app.route("/download", methods=["GET"])
def download_results():

    global latest_results

    if latest_results is None:

        return jsonify({

            "error": "No prediction results available."

        }), 404

    filename = "prediction_results.csv"

    latest_results.to_csv(
        filename,
        index=False
    )

    return send_from_directory(
        ".",
        filename,
        as_attachment=True
    )


# ============================================================
# Health Check
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "Online",
        "backend": "Flask",
        "version": "1.0",      
        "model": model_name
    })


# ============================================================
# Run Flask
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )