# audio_io.py
#
# Audio file loading and supported extensions.

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
    ".raw", ".voc", ".pvf", ".xi", ".htk", ".sd2", ".sph", ".nist", ".sf", ".mat",
)


def load_audio(path):
    if not path.lower().endswith(ACCEPT_EXTS):
        raise ValueError(f"Unsupported file type: {path}")
    data, sr = sf.read(path, always_2d=True)
    if data.dtype != np.float64:
        data = data.astype(np.float64)
    return data, sr
