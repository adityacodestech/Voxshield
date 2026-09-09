import os
import joblib
import pandas as pd

from detector import analyze_audio


# Load trained model
model_data = joblib.load("voice_detector.pkl")

model = model_data["model"]
features = model_data["features"]


def test_folder(folder, expected_label):

    print("\n================================")
    print(f"📂 TESTING: {folder}")
    print("================================")

    correct = 0
    total = 0

    for filename in sorted(os.listdir(folder)):

        if not filename.lower().endswith(".wav"):
            continue

        filepath = os.path.join(folder, filename)

        result = analyze_audio(filepath)

        X = pd.DataFrame([result])[features]

        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]

        predicted_label = "AI" if prediction == 1 else "REAL"

        confidence = probabilities[prediction] * 100

        status = "✅" if predicted_label == expected_label else "❌"

        print(
            f"{status} {filename:<20} "
            f"Predicted: {predicted_label:<5} "
            f"Confidence: {confidence:.1f}%"
        )

        if predicted_label == expected_label:
            correct += 1

        total += 1

    return correct, total


# Test REAL samples
real_correct, real_total = test_folder(
    "real_samples",
    "REAL"
)

# Test AI samples
ai_correct, ai_total = test_folder(
    "ai_samples",
    "AI"
)


total_correct = real_correct + ai_correct
total_samples = real_total + ai_total

print("\n================================")
print("📊 FINAL TEST RESULTS")
print("================================")

print(
    f"REAL: {real_correct}/{real_total} correct"
)

print(
    f"AI:   {ai_correct}/{ai_total} correct"
)

print(
    f"\nOverall: {total_correct}/{total_samples} correct"
)

print("================================")