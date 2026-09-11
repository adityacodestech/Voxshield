from backend.audio_pipeline import AudioPipeline


def create_audio_pipeline():
    """
    Create a new AudioPipeline for one audio stream.

    A separate pipeline is created for each WebSocket connection
    so that different calls do not share audio state.
    """
    return AudioPipeline()