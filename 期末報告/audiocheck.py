import numpy as np
import librosa

y, sr = librosa.load(r'C:\Users\user\Downloads\test_wavefile\audiocheck.net_dtmf__1_4_2_5_10dB\audiocheck.net_dtmf__1_4_2_5_30dB.wav', sr=None, mono=True)

low_freqs = [697, 770, 852, 941]
high_freqs = [1209, 1336, 1477, 1633]
dtmf_keys = {
    (697, 1209): '1', (697, 1336): '2', (697, 1477): '3', (697, 1633): 'A',
    (770, 1209): '4', (770, 1336): '5', (770, 1477): '6', (770, 1633): 'B',
    (852, 1209): '7', (852, 1336): '8', (852, 1477): '9', (852, 1633): 'C',
    (941, 1209): '*', (941, 1336): '0', (941, 1477): '#', (941, 1633): 'D',
}

frame_length = int(0.1 * sr)
hop_length = int(0.05 * sr)
tolerance = 5
min_interval = int(0.1 * sr)
max_digits = 100

def find_closest(freq_list, value, tolerance=10):
    closest = min(freq_list, key=lambda x: abs(x - value))
    return closest if abs(closest - value) <= tolerance else None

decoded_digits = []
last_digit = None
last_frame_index = -99999

for frame_idx in range(0, len(y) - frame_length, hop_length):
    frame = y[frame_idx:frame_idx + frame_length]

    freqs = np.fft.rfftfreq(len(frame), d=1/sr)
    spectrum = np.abs(np.fft.rfft(frame))

    top_indices = np.argsort(spectrum)[-5:]
    top_freqs = freqs[top_indices]

    matched_low = [find_closest(low_freqs, f, tolerance) for f in top_freqs if 650 < f < 1050]
    matched_high = [find_closest(high_freqs, f, tolerance) for f in top_freqs if 1100 < f < 1700]
    matched_low = [f for f in matched_low if f is not None]
    matched_high = [f for f in matched_high if f is not None]

    if matched_low and matched_high:
        key = dtmf_keys.get((matched_low[0], matched_high[0]))
        if key:
            if key != last_digit or (frame_idx - last_frame_index) > min_interval:
                decoded_digits.append(key)
                last_digit = key
                last_frame_index = frame_idx
