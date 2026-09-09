import wave
import numpy as np
import librosa


def analyze_audio(filepath):

    # -----------------------------
    # LOAD AUDIO
    # -----------------------------

    with wave.open(filepath, "rb") as audio:

        sample_rate = audio.getframerate()
        frames = audio.getnframes()
        audio_data = audio.readframes(frames)

    # Convert PCM → NumPy
    samples = np.frombuffer(
        audio_data,
        dtype=np.int16
    ).astype(np.float32) / 32768.0

    # -----------------------------
    # BASIC INFORMATION
    # -----------------------------

    duration = len(samples) / sample_rate

    # -----------------------------
    # RMS ENERGY
    # -----------------------------

    rms = np.mean(
        librosa.feature.rms(y=samples)
    )

    # -----------------------------
    # ZERO CROSSING RATE
    # -----------------------------

    zcr = np.mean(
        librosa.feature.zero_crossing_rate(samples)
    )

    # -----------------------------
    # SPECTRAL CENTROID
    # -----------------------------

    spectral_centroid = np.mean(
        librosa.feature.spectral_centroid(
            y=samples,
            sr=sample_rate
        )
    )

    # -----------------------------
    # SPECTRAL BANDWIDTH
    # -----------------------------

    spectral_bandwidth = np.mean(
        librosa.feature.spectral_bandwidth(
            y=samples,
            sr=sample_rate
        )
    )

    # -----------------------------
    # SPECTRAL ROLLOFF
    # -----------------------------

    spectral_rolloff = np.mean(
        librosa.feature.spectral_rolloff(
            y=samples,
            sr=sample_rate
        )
    )

    # -----------------------------
    # PITCH / F0
    # -----------------------------

    f0 = librosa.yin(
        samples,
        fmin=70,
        fmax=400,
        sr=sample_rate
    )

    valid_f0 = f0[
        np.isfinite(f0)
    ]

    if len(valid_f0) > 0:
        average_pitch = np.mean(valid_f0)
    else:
        average_pitch = 0

    # -----------------------------
    # PRINT RESULTS
    # -----------------------------

    print("\n================================")
    print("🎧 ADVANCED AUDIO ANALYSIS")
    print("================================")

    print(f"📁 File: {filepath}")
    print(f"🔊 Sample rate: {sample_rate} Hz")
    print(f"⏱️ Duration: {duration:.2f} seconds")

    print("\n📊 AUDIO FEATURES")
    print("--------------------------------")

    print(f"⚡ RMS Energy:       {rms:.4f}")
    print(f"〰️ Zero Crossing:    {zcr:.4f}")
    print(f"🎵 Average Pitch:    {average_pitch:.2f} Hz")
    print(f"📈 Spectral Centroid:{spectral_centroid:.2f} Hz")
    print(f"📊 Spectral Bandwidth:{spectral_bandwidth:.2f} Hz")
    print(f"📉 Spectral Rolloff: {spectral_rolloff:.2f} Hz")

    print("================================")

    return {
        "sample_rate": sample_rate,
        "duration": float(duration),
        "rms": float(rms),
        "zcr": float(zcr),
        "average_pitch": float(average_pitch),
        "spectral_centroid": float(spectral_centroid),
        "spectral_bandwidth": float(spectral_bandwidth),
        "spectral_rolloff": float(spectral_rolloff)
    }


# -----------------------------
# TEST
# -----------------------------

if __name__ == "__main__":

    file_path = "ai_samples/ai_001.wav"

    analyze_audio(file_path)

    print("\n✅ Advanced analysis complete!")