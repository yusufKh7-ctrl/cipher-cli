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
cipher ytdl info "playlist-url" --playlist   # numbered listing of all items

# Custom folder
cipher ytdl mp3 "URL" -o ~/Music/YouTube
```

Files are saved under `~/Downloads/Cipher/{Audio,Video,Thumbnails}` by default.
Playlist downloads are automatically prefixed (`01 - Title.mp3`, ...) to avoid
collisions. Commands exit with a non-zero code on failure, so they're safe to
use in scripts.

## Notes / Limitations

- YouTube changes protections often. Keep `yt-dlp` updated (`pip install -U yt-dlp`).
- A JavaScript runtime is **required** for YouTube downloads: install [deno](https://deno.com) (recommended) and make sure it's on your `PATH`. Without it, media URLs fail with HTTP 403.
- Age-restricted / members-only videos, or bot-check blocks on your IP? Pass cookies:

```bash
# read cookies straight from an installed browser
cipher ytdl mp3 "URL" --cookies-from-browser firefox
# ...or from a Netscape-format cookie file exported by a browser extension
cipher ytdl info "URL" --cookies ~/youtube-cookies.txt
```

- Thumbnail embedding requires ffmpeg and works best with mp3/m4a.
- This tool is for personal use. Respect copyright and YouTube ToS.

## Roadmap (honest)

- [x] Playlist resilience (skip broken items, numbered filenames)
- [x] Cookies support (`--cookies`, `--cookies-from-browser`)
- [ ] Config file for default quality / paths
- [ ] Concurrent playlist downloads
- [ ] Cookies / authenticated downloads helper

## License

No license file yet. Add one if you care.
