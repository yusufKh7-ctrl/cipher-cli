# Cipher CLI

A modular command-line toolkit. Currently focused on a solid YouTube (and yt-dlp sites) downloader.

## Features (ytdl)

- Download **audio** (mp3 / m4a / opus / flac...) with **embedded thumbnail + full metadata** by default
- Download **video** as MP4 with quality selection
- Optional separate thumbnail file
- Playlist support (or `--no-playlist`)
- `info` command to inspect metadata without downloading
- Custom output directory
- Nice Rich progress bars

## Requirements

- Python >= 3.11
- **ffmpeg** (required for audio extraction, thumbnail embedding, and merging)

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
winget install ffmpeg
```

## Install

```bash
git clone https://github.com/yusufKh7-ctrl/cipher-cli.git
cd cipher-cli
pip install -e .
# or with uv
uv sync
```

## Usage

```bash
# Show banner + commands
cipher

# Audio (MP3 320kbps + embedded cover art + metadata)
cipher ytdl mp3 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Best quality audio as m4a + keep thumbnail as separate file
cipher ytdl mp3 "URL" -q best -c m4a --keep-thumbnail

# Video 1080p + embed subtitles
cipher ytdl mp4 "URL" -q 1080p --embed-subs

# Only the single video from a playlist link
cipher ytdl mp3 "playlist-url" --no-playlist

# Inspect without downloading
cipher ytdl info "URL"

# Custom folder
cipher ytdl mp3 "URL" -o ~/Music/YouTube
```

Files are saved under `~/Downloads/Cipher/{Audio,Video,Thumbnails}` by default.

## Notes / Limitations

- YouTube changes protections often. Keep `yt-dlp` updated (`pip install -U yt-dlp`).
- Thumbnail embedding requires ffmpeg and works best with mp3/m4a.
- This tool is for personal use. Respect copyright and YouTube ToS.

## Roadmap (honest)

- [ ] hash / encoding commands (currently placeholders)
- [ ] Config file for default quality / paths
- [ ] Concurrent playlist downloads
- [ ] Cookies / authenticated downloads helper

## License

No license file yet. Add one if you care.
