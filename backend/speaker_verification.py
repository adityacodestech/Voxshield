import os
import numpy as np
import librosa


REFERENCE_FILE = "speaker_profiles/reference_voice.wav"


def extract_speaker_features(filepath):
    """
    Extract basic voice characteristics from an audio file.
    These features are used for the prototype speaker verification.
    """

    y, sr = librosa.load(filepath, sr=16000, mono=True)

    # Remove very quiet portions
    if len(y) == 0:
        raise ValueError("Audio file is empty.")

    # Basic acoustic features
    rms = float(np.mean(librosa.feature.rms(y=y)))
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=y)))

    pitch = librosa.yin(
        y,
        fmin=70,
        fmax=400,
        sr=sr
    )

    valid_pitch = pitch[np.isfinite(pitch)]

    if len(valid_pitch) > 0:
        average_pitch = float(np.mean(valid_pitch))
    else:
        average_pitch = 0.0

    spectral_centroid = float(
        np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    )

    spectral_bandwidth = float(
        np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
    )

    spectral_rolloff = float(
        np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
    )

    return np.array([
        rms,
        zcr,
        average_pitch,
        spectral_centroid,
        spectral_bandwidth,
        spectral_rolloff
    ])


def compare_speakers(reference_file, test_file):
    """
    Compare the reference voice with a test voice.

    Returns a similarity score from 0 to 100.
    """

    reference = extract_speaker_features(reference_file)
    test = extract_speaker_features(test_file)

    # Avoid division problems
    denominator = np.maximum(np.abs(reference), 1e-6)

    difference = np.abs(reference - test) / denominator

    # Average normalized difference
    average_difference = np.mean(difference)

    # Convert difference to similarity
    similarity = 100 * (1 / (1 + average_difference))

    return round(float(similarity), 2)


def verify_speaker(test_file):
    """
    Compare the incoming voice with the enrolled reference voice.
    """

    if not os.path.exists(REFERENCE_FILE):
        raise FileNotFoundError(
            f"Reference voice not found: {REFERENCE_FILE}"
        )

    similarity = compare_speakers(
        REFERENCE_FILE,
        test_file
    )

    # Prototype threshold
    if similarity >= 70:
        match = True
        reason = "Voice sufficiently matches the reference speaker."
    else:
        match = False
        reason = "Voice does not sufficiently match the reference speaker."

    return {
        "speaker_match_score": similarity,
        "speaker_match": match,
        "reason": reason
    }