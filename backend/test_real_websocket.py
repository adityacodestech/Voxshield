import asyncio
import wave
import websockets


AUDIO_FILE = "test_samples/real/real_test_01.wav"
WS_URL = "ws://127.0.0.1:8000/ws/audio"

FRAME_SAMPLES = 320
FRAME_BYTES = 640
FRAME_DURATION = 0.020


async def main():

    print("\n================================")
    print("🎤 REAL HUMAN VOICE WEBSOCKET TEST")
    print("================================")
    print(f"Audio file: {AUDIO_FILE}")

    with wave.open(AUDIO_FILE, "rb") as wav:

        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()

        print(f"Sample rate : {sample_rate}")
        print(f"Channels    : {channels}")
        print(f"Sample width: {sample_width * 8}-bit")

        audio_data = wav.readframes(wav.getnframes())


    print("\n🔌 Connecting to VoxShield backend...")

    async with websockets.connect(WS_URL) as websocket:

        print("✅ WebSocket connected")

        for i in range(
            0,
            len(audio_data),
            FRAME_BYTES
        ):

            frame = audio_data[
                i:i + FRAME_BYTES
            ]

            if len(frame) < FRAME_BYTES:
                break

            await websocket.send(frame)

            await asyncio.sleep(
                FRAME_DURATION
            )


        print("📤 REAL HUMAN audio sent")

        # Send silence to trigger VAD termination
        silence = b"\x00" * FRAME_BYTES

        for _ in range(30):

            await websocket.send(silence)

            await asyncio.sleep(
                FRAME_DURATION
            )


        print("⏳ Waiting for VoxShield result...")

        try:

            result = await asyncio.wait_for(
                websocket.recv(),
                timeout=10
            )

            print("\n================================")
            print("📥 VOXSHIELD RESULT")
            print("================================")
            print(result)
            print("================================")

        except asyncio.TimeoutError:

            print(
                "❌ Timed out waiting for result."
            )


if __name__ == "__main__":
    asyncio.run(main())