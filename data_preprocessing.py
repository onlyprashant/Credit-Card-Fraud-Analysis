import joblib
import pandas as pd
from sklearn.preprocessing import RobustScaler

# ======================================================
# Configuration
# ======================================================

DATASET_PATH = "creditcard.csv"

TIME_SCALER_PATH = "time_scaler.pkl"
AMOUNT_SCALER_PATH = "amount_scaler.pkl"

V_COLUMNS = [f"V{i}" for i in range(1, 29)]

FEATURE_COLUMNS = [
    "Time_scaled",
    "Amount_scaled",
    "Hour",
    "High_Amount"
] + V_COLUMNS


# ======================================================
# Load Dataset
# ======================================================

def load_data(path=DATASET_PATH):

    df = pd.read_csv(path)

    print("=" * 60)
    print("Dataset Loaded Successfully")
    print("=" * 60)

    print(f"Shape : {df.shape}")

    print("\nClass Distribution")
    print(df["Class"].value_counts())

    return df


# ======================================================
# Fit & Save Scalers (Training)
# ======================================================

def fit_scalers(df):

    time_scaler = RobustScaler()
    amount_scaler = RobustScaler()

    df["Time_scaled"] = time_scaler.fit_transform(df[["Time"]])
    df["Amount_scaled"] = amount_scaler.fit_transform(df[["Amount"]])

    joblib.dump(time_scaler, TIME_SCALER_PATH)
    joblib.dump(amount_scaler, AMOUNT_SCALER_PATH)

    print("Scalers saved successfully.")

    return df


# ======================================================
# Load Saved Scalers (Inference)
# ======================================================

def transform_scalers(df):

    time_scaler = joblib.load(TIME_SCALER_PATH)
    amount_scaler = joblib.load(AMOUNT_SCALER_PATH)

    df["Time_scaled"] = time_scaler.transform(df[["Time"]])
    df["Amount_scaled"] = amount_scaler.transform(df[["Amount"]])

    return df


# ======================================================
# Feature Engineering
# ======================================================

def engineer_features(df):

    df["Hour"] = (df["Time"] % (24 * 3600)) // 3600

    df["High_Amount"] = (
        df["Amount_scaled"] > 3
    ).astype(int)

    return df


# ======================================================
# Training Preprocessing
# ======================================================

def preprocess_training_data(df):

    df = fit_scalers(df)

    df = engineer_features(df)

    df.drop(columns=["Time", "Amount"], inplace=True)

    df = df[FEATURE_COLUMNS + ["Class"]]

    print("\nTraining preprocessing complete.")

    return df


# ======================================================
# Single Transaction Preprocessing
# ======================================================

def preprocess_transaction(transaction):
    """
    Preprocess a single transaction (dict)
    OR multiple transactions (list of dicts).
    """

    # Single transaction
    if isinstance(transaction, dict):
        df = pd.DataFrame([transaction])

    # Multiple transactions (CSV upload)
    elif isinstance(transaction, list):
        df = pd.DataFrame(transaction)

    else:
        raise ValueError(
            "Input must be a dictionary or a list of dictionaries."
        )

    df = transform_scalers(df)

    df = engineer_features(df)

    df.drop(columns=["Time", "Amount"], inplace=True)

    df = df[FEATURE_COLUMNS]

    return df


# ======================================================
# Test
# ======================================================

if __name__ == "__main__":

    df = load_data()

    df = preprocess_training_data(df)

    print("\nProcessed Dataset")
    print(df.head())

    print("\nFinal Features")
    print(df.columns.tolist())