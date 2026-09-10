import os
import joblib
import pandas as pd

from detector import analyze_audio

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_FILE = "voice_detector.pkl"

REAL_FOLDER = "test_samples/real"
AI_FOLDER = "test_samples/ai"


# ============================================================
# LOAD MODEL
# ============================================================

print("\n================================")
print("📊 VOICE DETECTION EVALUATION")
print("================================")

model_data = joblib.load(MODEL_FILE)

model = model_data["model"]

features = model_data["features"]

print("✅ Model loaded successfully")


# ============================================================
# STORE RESULTS
# ============================================================

results = []


# ============================================================
# TEST FUNCTION
# ============================================================

def evaluate_folder(folder, actual_label):

    if not os.path.exists(folder):

        print(
            f"❌ Folder not found: {folder}"
        )

        return


    files = sorted(
        os.listdir(folder)
    )


    for filename in files:

        if not filename.lower().endswith(".wav"):

            continue


        filepath = os.path.join(
            folder,
            filename
        )


        try:

            # -----------------------------------------------
            # Extract audio features
            # -----------------------------------------------

            feature_data = analyze_audio(
                filepath
            )


            # -----------------------------------------------
            # Prepare model input
            # -----------------------------------------------

            X = pd.DataFrame(
                [feature_data]
            )[features]


            # -----------------------------------------------
            # Prediction
            # -----------------------------------------------

            prediction = model.predict(X)[0]


            probabilities = (
                model.predict_proba(X)[0]
            )


            real_score = (
                probabilities[0] * 100
            )


            ai_score = (
                probabilities[1] * 100
            )


            predicted_label = (
                "AI"
                if prediction == 1
                else "REAL"
            )


            # -----------------------------------------------
            # Check correctness
            # -----------------------------------------------

            correct = (
                predicted_label ==
                actual_label
            )


            results.append({

                "file": filename,

                "actual": actual_label,

                "predicted": predicted_label,

                "real_score": round(
                    real_score,
                    2
                ),

                "ai_score": round(
                    ai_score,
                    2
                ),

                "correct": correct

            })


        except Exception as e:

            print(
                f"❌ Error processing {filename}: {e}"
            )


# ============================================================
# EVALUATE REAL SAMPLES
# ============================================================

print("\n🎙️ Testing REAL voice samples...")

evaluate_folder(
    REAL_FOLDER,
    "REAL"
)


# ============================================================
# EVALUATE AI SAMPLES
# ============================================================

print("\n🤖 Testing AI voice samples...")

evaluate_folder(
    AI_FOLDER,
    "AI"
)


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(results)


if len(df) == 0:

    print(
        "\n❌ No WAV files found."
    )

    exit()


# ============================================================
# CONVERT LABELS
# ============================================================

y_true = df["actual"].map({

    "REAL": 0,

    "AI": 1

})


y_pred = df["predicted"].map({

    "REAL": 0,

    "AI": 1

})


# ============================================================
# CALCULATE METRICS
# ============================================================

accuracy = accuracy_score(
    y_true,
    y_pred
)


precision = precision_score(
    y_true,
    y_pred,
    zero_division=0
)


recall = recall_score(
    y_true,
    y_pred,
    zero_division=0
)


f1 = f1_score(
    y_true,
    y_pred,
    zero_division=0
)


cm = confusion_matrix(
    y_true,
    y_pred
)


# ============================================================
# PRINT INDIVIDUAL RESULTS
# ============================================================

print("\n================================")
print("🧪 INDIVIDUAL TEST RESULTS")
print("================================")

print(
    df.to_string(
        index=False
    )
)


# ============================================================
# PRINT SUMMARY
# ============================================================

print("\n================================")
print("📈 EVALUATION SUMMARY")
print("================================")


print(
    f"Total Samples : {len(df)}"
)


print(
    f"Correct       : {df['correct'].sum()}"
)


print(
    f"Incorrect     : "
    f"{len(df) - df['correct'].sum()}"
)


print(
    f"\nAccuracy      : "
    f"{accuracy * 100:.2f}%"
)


print(
    f"Precision     : "
    f"{precision * 100:.2f}%"
)


print(
    f"Recall        : "
    f"{recall * 100:.2f}%"
)


print(
    f"F1-Score      : "
    f"{f1 * 100:.2f}%"
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\n================================")
print("🔲 CONFUSION MATRIX")
print("================================")

print(
    "                 Predicted"
)

print(
    "               REAL    AI"
)

print(
    f"Actual REAL    "
    f"{cm[0][0]:4d}   "
    f"{cm[0][1]:4d}"
)

print(
    f"Actual AI      "
    f"{cm[1][0]:4d}   "
    f"{cm[1][1]:4d}"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n================================")
print("📋 CLASSIFICATION REPORT")
print("================================")

print(
    classification_report(
        y_true,
        y_pred,
        target_names=[
            "REAL",
            "AI"
        ],
        zero_division=0
    )
)


# ============================================================
# SAVE CSV REPORT
# ============================================================

REPORT_FILE = "evaluation_results.csv"


df.to_csv(
    REPORT_FILE,
    index=False
)


print("\n================================")
print("💾 REPORT SAVED")
print("================================")

print(
    f"File: {REPORT_FILE}"
)

print("\n✅ Evaluation completed successfully.")