# Add or Subtract Stems

A desktop application for combining and subtracting audio stems. Built with Python and PyQt5.

![Screenshot](screenshot.png)

[![Cross-platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/smcconne/Add-or-Subtract-Stems/releases)

## What it does

**Add or Subtract Stems** lets you manipulate audio files by adding (mixing) or subtracting stems from a song. This is useful for:

- **Isolating leftover artifacts** – Most AI stem separation tools leave out pieces of the original audio, meaning if you add the separated stems together they won't sum to equal the input audio, which you can verify with this tool. 
- **Combining stems** – Mix multiple audio files together, allowing you to (for example) mix leftover artifacts into one of your stems or average the results from multiple algorithms - (for those unaware, -6db = half amplitude, so combining two stems @ -6db is the same as averaging the two stems, useful for averaging the results of two AI algorithms)

## Features

### Add Stems Tab
- Drag and drop multiple audio files to combine them
- Option to lower volume before summing (0dB, -1dB, or -6dB)
- Automatic clipping detection with the option to reduce volume or to let it clip
- Single file mode for simple volume reduction or format conversion

### Subtract Stems Tab
- Drag your original song on the left
- Drag the stems you want to remove on the right
- The app subtracts the stems from the original, leaving you with what remains

### Additional Features
- **Multiple output formats**: Export as FLAC or WAV. Why only lossless output? Because the only way to get a perfect sum is with a lossless format. Try to avoid using .mp3 for AI stem separation, it won't do as good a job as FLAC or WAV
- **Customizable themes**: Choose from a variety of color themes organized by color category
- **Cross-platform**: Works on Windows, macOS, and Linux

## Supported Audio Formats

- WAV, W64
- AIFF, AIF, AIFC
- FLAC
- OGG, OGA, Opus
- MP3
- AU, SND, CAF
- And more (RAW, VOC, PVF, XI, HTK, SD2, SPH, NIST, SF, MAT)

## Installation

### Download Pre-built Binaries

Download the latest release for your platform from the [Releases](../../releases) page.

### Build from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/smcconne/Add-or-Subtract-Stems.git
   cd Add-or-Subtract-Stems
   ```

2. Install dependencies:
   ```bash
   pip install PyQt5 numpy soundfile
   ```

3. Run the application:
   ```bash
   python "Add or Subtract Stems.py"
   ```

### Build Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller "Add or Subtract Stems.spec" --noconfirm
```

The executable will be in the `dist` folder.

## Usage

1. **Launch the app**
2. **Choose a tab**:
   - **Add Stems**: For combining audio files or adjusting volume
   - **Subtract Stems**: For removing stems from a song
3. **Drag and drop** your audio files into the drop zones
4. **Select options** (volume reduction, output format)
5. **Click the action button** to process
6. **Find your output** in the same folder as your input files

## How Stem Subtraction Works

When you subtract stems from a song, the app performs sample-by-sample subtraction. This works best when:

- The stems were originally extracted from the exact same mix
- The audio files have matching sample rates
- The stems are properly aligned (same starting point)

> **Note**: This is phase-cancellation subtraction - for best results, use stems that were split from the same master file.

## License

This project is open source.

## Credits

- App icon by [Pop Vectors](https://www.flaticon.com/authors/pop-vectors)
