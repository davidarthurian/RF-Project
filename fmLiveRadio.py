from rtlsdr import RtlSdr
import numpy as np
import scipy.signal as signal
import sounddevice as sd
import threading
import queue
import time


# -----------------------------
# Configuration
# -----------------------------
SAMPLE_RATE = 1.024e6        # lower SDR sample rate for fewer USB overflows
AUDIO_RATE = 48_000
RF_OFFSET = 200e3            # tune above station to avoid DC spike
GAIN = 20
CHUNK_DURATION = 0.05        # smaller chunks reduce libusb overflow risk
CHANNEL_CUTOFF_HZ = 120e3
AUDIO_CUTOFF_HZ = 15e3
VOLUME = 0.30


station_queue = queue.Queue()
stop_event = threading.Event()


def fm_demodulate(iq_samples):
    return np.angle(iq_samples[1:] * np.conj(iq_samples[:-1]))


def apply_deemphasis(audio, fs, tau=75e-6):
    alpha = np.exp(-1 / (fs * tau))
    b = [1 - alpha]
    a = [1, -alpha]
    return signal.lfilter(b, a, audio)


def process_fm_chunk(samples, sample_rate, rf_offset):
    t = np.arange(len(samples)) / sample_rate

    # Station is below SDR center by RF_OFFSET, so shift it up to baseband.
    shifted = samples * np.exp(2j * np.pi * rf_offset * t)

    channel_filter = signal.firwin(
        numtaps=129,
        cutoff=CHANNEL_CUTOFF_HZ,
        fs=sample_rate
    )

    filtered = signal.lfilter(channel_filter, 1.0, shifted)

    # Downsample 1.024 MHz -> 256 kHz
    iq_downsampled = signal.resample_poly(filtered, up=1, down=4)
    iq_rate = sample_rate / 4

    demodulated = fm_demodulate(iq_downsampled)

    audio_filter = signal.firwin(
        numtaps=129,
        cutoff=AUDIO_CUTOFF_HZ,
        fs=iq_rate
    )

    audio_filtered = signal.lfilter(audio_filter, 1.0, demodulated)
    audio_deemphasized = apply_deemphasis(audio_filtered, fs=iq_rate)

    # Resample 256 kHz -> 48 kHz
    audio = signal.resample_poly(audio_deemphasized, up=3, down=16)

    audio = audio - np.mean(audio)

    rms = np.sqrt(np.mean(audio ** 2)) + 1e-12
    audio = audio / (8 * rms)

    audio = audio * VOLUME
    audio = np.clip(audio, -1.0, 1.0)

    return audio.astype(np.float32)


def input_thread():
    print("\nLive tuning controls:")
    print("  Type a frequency in MHz and press Enter, e.g. 88.5")
    print("  Type q and press Enter to quit\n")

    while not stop_event.is_set():
        user_input = input("> ").strip()

        if user_input.lower() in ["q", "quit", "exit"]:
            stop_event.set()
            break

        try:
            station_queue.put(float(user_input))
        except ValueError:
            print("Invalid input. Type a frequency like 88.5 or q to quit.")


def run_live_fm_radio(initial_station_mhz=88.5):
    station_mhz = initial_station_mhz
    center_freq_hz = station_mhz * 1e6 + RF_OFFSET

    sdr = None

    try:
        print("Opening RTL-SDR...")
        sdr = RtlSdr()
        sdr.sample_rate = SAMPLE_RATE
        sdr.center_freq = center_freq_hz
        sdr.gain = GAIN

        chunk_samples = int(SAMPLE_RATE * CHUNK_DURATION)

        print("Starting live FM receiver")
        print(f"Initial station: {station_mhz:.3f} MHz")
        print(f"RTL-SDR center frequency: {center_freq_hz / 1e6:.3f} MHz")
        print(f"Sample rate: {SAMPLE_RATE / 1e6:.3f} MS/s")
        print(f"Gain: {GAIN} dB")
        print(f"Chunk duration: {CHUNK_DURATION} sec")
        print("Lower your Mac volume before listening.\n")

        tuner_thread = threading.Thread(target=input_thread, daemon=True)
        tuner_thread.start()

        with sd.OutputStream(
            samplerate=AUDIO_RATE,
            channels=1,
            dtype="float32"
        ) as stream:

            while not stop_event.is_set():
                while not station_queue.empty():
                    station_mhz = station_queue.get()
                    center_freq_hz = station_mhz * 1e6 + RF_OFFSET

                    print(f"\nTuning to {station_mhz:.3f} MHz...")
                    sdr.center_freq = center_freq_hz
                    time.sleep(0.2)

                try:
                    samples = sdr.read_samples(chunk_samples)
                except Exception as e:
                    print(f"SDR read error, retrying: {e}")
                    time.sleep(0.1)
                    continue

                audio = process_fm_chunk(
                    samples=samples,
                    sample_rate=SAMPLE_RATE,
                    rf_offset=RF_OFFSET
                )

                stream.write(audio.reshape(-1, 1))

    finally:
        print("\nClosing radio...")
        if sdr is not None:
            sdr.close()


if __name__ == "__main__":
    run_live_fm_radio(initial_station_mhz=88.5)