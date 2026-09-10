import os
import joblib
import pandas as pd
from detector import analyze_audio

MODEL_FILE = "voice_detector.pkl"

TEST_REAL_FOLDER = "test_samples/real"
TEST_AI_FOLDER = "test_samples/ai"

# Load trained model
model_data = joblib.load(MODEL_FILE)

model = model_data["model"]
features = model_data["features"]

results = []


def test_folder(folder, actual_label):

    if not os.path.exists(folder):
        print(f"Folder not found: {folder}")
        return

    for filename in os.listdir(folder):

        if not filename.lower().endswith(".wav"):
            continue

        filepath = os.path.join(folder, filename)

        try:
            feature_data = analyze_audio(filepath)

            X = pd.DataFrame([feature_data])[features]

            prediction = model.predict(X)[0]

            probabilities = model.predict_proba(X)[0]

            real_score = probabilities[0] * 100
            ai_score = probabilities[1] * 100

            predicted_label = "AI" if prediction == 1 else "REAL"

            correct = predicted_label == actual_label

            results.append({
                "file": filename,
                "actual": actual_label,
                "predicted": predicted_label,
                "real_score": round(real_score, 2),
                "ai_score": round(ai_score, 2),
                "correct": correct
            })

        except Exception as e:

            print(f"Error processing {filename}: {e}")


# Test REAL samples
test_folder(TEST_REAL_FOLDER, "REAL")

# Test AI samples
test_folder(TEST_AI_FOLDER, "AI")


# Display results
df = pd.DataFrame(results)

print("\n================================")
print("🧪 UNSEEN TEST RESULTS")
print("================================")

if len(df) == 0:

    print("No test files found.")

else:

    print(df.to_string(index=False))

    accuracy = df["correct"].mean() * 100

    print("\n--------------------------------")
    print(f"Test Samples : {len(df)}")
    print(f"Correct      : {df['correct'].sum()}")
    print(f"Accuracy     : {accuracy:.2f}%")
    print("--------------------------------")