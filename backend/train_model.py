import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# ---------------------------------------
# LOAD DATASET
# ---------------------------------------

df = pd.read_csv("dataset.csv")

print("================================")
print("DATASET")
print("================================")

print("Total samples:", len(df))
print("\nClass distribution:")
print(df["label"].value_counts())


# ---------------------------------------
# FEATURES
# ---------------------------------------

features = [
    "rms",
    "zcr",
    "average_pitch",
    "spectral_centroid",
    "spectral_bandwidth",
    "spectral_rolloff"
]

X = df[features]
y = df["label"]


# ---------------------------------------
# TRAIN / TEST SPLIT
# ---------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)


print("\n================================")
print("TRAIN / TEST SPLIT")
print("================================")

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# ---------------------------------------
# TRAIN RANDOM FOREST
# ---------------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)


# ---------------------------------------
# TEST MODEL
# ---------------------------------------

y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)


print("\n================================")
print("MODEL PERFORMANCE")
print("================================")

print(
    f"Test Accuracy: {accuracy * 100:.2f}%"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "REAL",
            "AI"
        ]
    )
)


print("Confusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ---------------------------------------
# SAVE MODEL
# ---------------------------------------

model_data = {
    "model": model,
    "features": features
}

joblib.dump(
    model_data,
    "voice_detector.pkl"
)


print("\n================================")
print("MODEL SAVED")
print("================================")

print(
    "voice_detector.pkl created successfully!"
)