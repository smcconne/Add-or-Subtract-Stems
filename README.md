# Add or Subtract Stems

A desktop application for combining and subtracting audio stems. Built with Python and PyQt5.

![Screenshot](app_screenshot.png)

[![Cross-platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/smcconne/Add-or-Subtract-Stems/releases)

## What it does

**Add or Subtract Stems** lets you manipulate audio files by adding (mixing) or subtracting stems from a song. This is useful for:

- **Isolating leftover artifacts** – The majority of AI stem separation tools leave out pieces of the original audio. Just try adding the separated stems back together, they won't quite equal the input audio - some algorithms leave more out than others but in general AI stems *aren't complete* until you subtract them from the song you started with and spit out what's left. The Subtract Stems part of this tool greatly speeds up this task compared to using a DAW.
- **Combining stems** – Mix multiple audio files together, allowing you to (for example) mix leftover artifacts back into one of your stems or average the results from multiple algorithms - (for those unaware, -6db = half amplitude, so combining two stems @ -6db is the same as averaging the two stems, useful for averaging the results of two AI algorithms)
- **Lowering volume before unmixing** – Before running AI stem separation algorithms, you will get better results if you first lower the volume because it helps avoid clipped output audio. To do this quickly and easily, I made it so you can just drag a single file into the Add Stems tab and select how much you want to lower the volume.
  
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

### Build from Source (Developers/Contributors)

1. Clone the repository:
   ```bash
   git clone https://github.com/smcconne/Add-or-Subtract-Stems.git
   cd Add-or-Subtract-Stems
   ```

2. Create and activate a virtual environment (recommended, keeps the project's packages isolated from your global Python install):

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python "Add or Subtract Stems.py"
   ```

Live theme reload is built in:
   - While the app is running, save changes to `themes_data.py` or `theming.py`
   - The current theme is re-applied automatically without restarting the app

### Build Executable (Developers/Contributors)

Github Actions are set up to build executables for Windows, Mac, and Linux when you use `git tag` with an incremented version #:

```bash
# Example: bump from v1.2.3 to v1.2.4
git fetch --tags
git tag v1.2.4
git push origin v1.2.4
```

To create a standalone executable without Github Actions:

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
4. **Select options**: volume reduction, output format
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
