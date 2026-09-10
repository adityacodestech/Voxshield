import os
import pandas as pd
from detector import analyze_audio

DATASET = []

# -----------------------------
# Process REAL samples
# -----------------------------
real_folder = "real_samples"

for filename in os.listdir(real_folder):

    if filename.lower().endswith(".wav"):

        filepath = os.path.join(real_folder, filename)

        print(f"Processing REAL: {filename}")

        features = analyze_audio(filepath)

        features["label"] = 0
        features["type"] = "REAL"
        features["file"] = filename

        DATASET.append(features)


# -----------------------------
# Process AI samples
# -----------------------------
ai_folder = "ai_samples"

for filename in os.listdir(ai_folder):

    if filename.lower().endswith(".wav"):

        filepath = os.path.join(ai_folder, filename)

        print(f"Processing AI: {filename}")

        features = analyze_audio(filepath)

        features["label"] = 1
        features["type"] = "AI"
        features["file"] = filename

        DATASET.append(features)


# -----------------------------
# Create DataFrame
# -----------------------------
df = pd.DataFrame(DATASET)

# Put label/type/file at the end
columns = [
    "file",
    "type",
    "label",
    "sample_rate",
    "duration",
    "rms",
    "zcr",
    "average_pitch",
    "spectral_centroid",
    "spectral_bandwidth",
    "spectral_rolloff"
]

df = df[columns]

# Save dataset
df.to_csv("dataset.csv", index=False)

print("\n================================")
print("✅ DATASET CREATED")
print("================================")

print(f"Total samples: {len(df)}")
print(f"Real samples:  {(df['label'] == 0).sum()}")
print(f"AI samples:    {(df['label'] == 1).sum()}")

print("\n📁 Saved as: dataset.csv")

print("\nDataset preview:")
print(df.to_string(index=False))