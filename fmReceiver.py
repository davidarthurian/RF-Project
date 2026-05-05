from rtlsdr import RtlSdr
import numpy as np
import scipy.signal as signal
from scipy.io import wavfile
import subprocess
import argparse


def fm_demodulate(iq_samples):
    """
    Wideband FM demodulation using phase difference between adjacent IQ samples.
    """
    return np.angle(iq_samples[1:] * np.conj(iq_samples[:-1]))


def normalize_audio(audio, scale=8000):
    """
    Normalize audio safely to int16.
    Lower scale avoids blasting loud static.
    """
    audio = audio - np.mean(audio)
    max_val = np.max(np.abs(audio))

    if max_val > 0:
        audio = audio / max_val

    return np.int16(audio * scale)


def receive_fm_station(
    station_mhz,
    duration_sec=5,
    output_file="fm_output.wav",
    sample_rate=2.4e6,
    rf_offset=250e3,
    gain=20,
):
    station_hz = station_mhz * 1e6

    # Tune slightly above station to avoid RTL-SDR DC spike at exact center.
    rtl_center_freq = station_hz + rf_offset

    print(f"Target station: {station_mhz:.3f} MHz")
    print(f"RTL-SDR tuned to: {rtl_center_freq / 1e6:.3f} MHz")
    print(f"RF offset: {rf_offset / 1e3:.1f} kHz")
    print(f"Sample rate: {sample_rate / 1e6:.2f} MS/s")
    print(f"Gain: {gain} dB")
    print(f"Recording duration: {duration_sec} sec")
    print("Capturing samples...")

    sdr = None

    try:
        sdr = RtlSdr()
        sdr.sample_rate = sample_rate
        sdr.center_freq = rtl_center_freq
        sdr.gain = gain

        num_samples = int(sample_rate * duration_sec)
        samples = sdr.read_samples(num_samples)

    finally:
        if sdr is not None:
            sdr.close()

    print("Samples captured.")
    print("Digitally shifting station to baseband...")

    # Shift desired station from -rf_offset back to 0 Hz/baseband.
    # Since SDR is tuned above the target station, the station appears at -rf_offset.
    t = np.arange(len(samples)) / sample_rate
    shifted = samples * np.exp(2j * np.pi * rf_offset * t)

    print("Filtering FM channel...")

    # FM broadcast stations can occupy roughly 150-200 kHz.
    # This keeps the station while rejecting nearby signals.
    channel_cutoff_hz = 120e3
    channel_filter = signal.firwin(
        numtaps=257,
        cutoff=channel_cutoff_hz,
        fs=sample_rate
    )

    filtered = signal.lfilter(channel_filter, 1.0, shifted)

    print("Downsampling IQ...")

    # Downsample 2.4 MHz -> 240 kHz
    iq_downsampled = signal.resample_poly(filtered, up=1, down=10)
    iq_rate = sample_rate / 10

    print("FM demodulating...")

    demodulated = fm_demodulate(iq_downsampled)

    print("Filtering audio...")

    # Broadcast FM audio is roughly 30 Hz to 15 kHz.
    audio_cutoff_hz = 15e3
    audio_filter = signal.firwin(
        numtaps=257,
        cutoff=audio_cutoff_hz,
        fs=iq_rate
    )

    audio_filtered = signal.lfilter(audio_filter, 1.0, demodulated)

    # Remove DC offset again after demod/filter
    audio_filtered = audio_filtered - np.mean(audio_filtered)

    print("Resampling audio to 48 kHz...")

    # 240 kHz -> 48 kHz
    audio_rate = 48_000
    audio = signal.resample_poly(audio_filtered, up=1, down=5)

    audio_int16 = normalize_audio(audio, scale=8000)

    wavfile.write(output_file, audio_rate, audio_int16)

    print(f"Saved audio to: {output_file}")

    try:
        print("Playing audio...")
        subprocess.run(["afplay", output_file])
    except Exception:
        print("Could not auto-play audio. Open the WAV file manually.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RTL-SDR FM Broadcast Receiver")

    parser.add_argument(
        "--station",
        type=float,
        default=88.5,
        help="FM station frequency in MHz, e.g. 88.5"
    )

    parser.add_argument(
        "--duration",
        type=float,
        default=5,
        help="Recording duration in seconds"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="wamu_88_5.wav",
        help="Output WAV filename"
    )

    parser.add_argument(
        "--gain",
        type=float,
        default=20,
        help="RTL-SDR gain in dB"
    )

    args = parser.parse_args()

    receive_fm_station(
        station_mhz=args.station,
        duration_sec=args.duration,
        output_file=args.output,
        gain=args.gain
    )