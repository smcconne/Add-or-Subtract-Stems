# audio_io.py
#
# Audio file loading and supported extensions.

import io
import os
import numpy as np
import soundfile as sf


ACCEPT_EXTS = (
    ".wav", ".w64",
    ".aif", ".aiff", ".aifc",
    ".au", ".snd",
    ".caf",
    ".flac",
    ".ogg", ".oga", ".opus",
    ".mp3",
    ".m4a", ".aac", ".alac",
    ".ape", ".wma", ".wv", ".mpc", ".tta", ".ac3", ".dts", ".amr",
    ".raw", ".voc", ".pvf", ".xi", ".htk", ".sd2", ".sph", ".nist", ".sf", ".mat",
)

# Extensions that require pydub (ffmpeg) instead of soundfile
_PYDUB_EXTS = (".m4a", ".aac", ".alac", ".ape", ".wma", ".wv", ".mpc", ".tta", ".ac3", ".dts", ".amr")


def _load_via_pydub(path):
    """Decode audio via pydub/ffmpeg and return (np.float64 array, sample_rate)."""
    from pydub import AudioSegment

    seg = AudioSegment.from_file(path)
    sr = seg.frame_rate
    channels = seg.channels
    samples = np.array(seg.get_array_of_samples(), dtype=np.float64)
    # pydub returns interleaved samples; reshape to (frames, channels)
    samples = samples.reshape(-1, channels)
    # Normalise to [-1, 1] based on sample width
    max_val = float(1 << (seg.sample_width * 8 - 1))
    samples /= max_val
    return samples, sr


def load_audio(path):
    if not path.lower().endswith(ACCEPT_EXTS):
        raise ValueError(f"Unsupported file type: {path}")
    if path.lower().endswith(_PYDUB_EXTS):
        return _load_via_pydub(path)
    data, sr = sf.read(path, always_2d=True)
    if data.dtype != np.float64:
        data = data.astype(np.float64)
    return data, sr
