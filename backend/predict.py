import joblib
import pandas as pd

from detector import analyze_audio


# Load trained model
model_data = joblib.load("voice_detector.pkl")

model = model_data["model"]
features = model_data["features"]


def predict_voice(filepath):

    print("\n================================")
    print("🎧 AI VOICE DETECTION")
    print("================================")

    # Extract audio features
    result = analyze_audio(filepath)

    # Create dataframe with exactly the features used during training
    X = pd.DataFrame([result])[features]

    # Prediction
    prediction = model.predict(X)[0]

    # Probability
    probabilities = model.predict_proba(X)[0]

    real_probability = probabilities[0] * 100
    ai_probability = probabilities[1] * 100

    print("\n================================")
    print("🔍 DETECTION RESULT")
    print("================================")

    if prediction == 1:
        print("🤖 Prediction: AI GENERATED VOICE")
    else:
        print("👤 Prediction: REAL HUMAN VOICE")

    print(f"👤 REAL Probability: {real_probability:.2f}%")
    print(f"🤖 AI Probability:   {ai_probability:.2f}%")

    print("================================")

    return {
        "prediction": "AI" if prediction == 1 else "REAL",
        "real_probability": real_probability,
        "ai_probability": ai_probability
    }


if __name__ == "__main__":

    # Change this file when testing another audio
    file_path = "ai_samples/ai_001.wav"

    predict_voice(file_path)