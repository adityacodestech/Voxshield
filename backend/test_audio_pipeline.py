from audio_pipeline import (
    AudioPipeline,
    SAMPLE_RATE,
    FRAME_BYTES
)

import webrtcvad


def test_pipeline_creation():

    vad = webrtcvad.Vad()
    vad.set_mode(2)

    pipeline = AudioPipeline(vad)

    assert pipeline is not None

    print("✅ AudioPipeline created successfully")


def test_frame_configuration():

    assert SAMPLE_RATE == 16000

    assert FRAME_BYTES == 640

    print("✅ Audio format configuration verified")


def test_speech_frame_processing():

    vad = webrtcvad.Vad()
    vad.set_mode(2)

    pipeline = AudioPipeline(vad)

    # A silent 20 ms frame
    silence = b"\x00" * FRAME_BYTES

    result = pipeline.process_frame(silence)

    # Silence alone should not create a speech segment
    assert result is None

    print("✅ Speech frame processing verified")


def test_pipeline_reset():

    vad = webrtcvad.Vad()
    vad.set_mode(2)

    pipeline = AudioPipeline(vad)

    assert pipeline.speech_chunks == 0
    assert pipeline.silence_chunks == 0
    assert len(pipeline.speech_buffer) == 0

    print("✅ Pipeline initial state verified")


if __name__ == "__main__":

    test_pipeline_creation()

    test_frame_configuration()

    test_speech_frame_processing()

    test_pipeline_reset()

    print("\n🎤 Student 2 audio pipeline tests passed")