# CI Docker Configuration

This directory contains the Docker configuration for building and running the pole-crawler in a CI environment.

## Usage

The Dockerfile is designed to:
1. Create an Instagram session using `pole_crawler/make_session.py` with environment variables
2. Run the main crawler application with command-line arguments

### Environment Variables

When running the container, you need to set these environment variables:

#### Instagram Session Variables:
- `INSTAGRAM_CSRFTOKEN`: Instagram CSRF token
- `INSTAGRAM_SESSIONID`: Instagram session ID  
- `INSTAGRAM_DS_USER_ID`: Instagram user ID
- `INSTAGRAM_IG_DID`: Instagram device ID
- `INSTAGRAM_USERNAME`: Instagram username (default: "adeveloper266")
- `SESSION_FILE_PATH`: Path where the session file will be saved

#### Crawler Arguments:
- `CRAWLER_ARGS`: Command-line arguments for main.py (passed as a string)

### Persistent Storage

Images downloaded by the crawler are stored in the `downloads` directory inside the container. To persist these images beyond the container lifecycle, you should mount a volume when running the container:

```bash
# Run with persistent storage
docker run \
  -e INSTAGRAM_CSRFTOKEN="your_csrf_token" \
  -e INSTAGRAM_SESSIONID="your_session_id" \
  -e INSTAGRAM_DS_USER_ID="your_user_id" \
  -e INSTAGRAM_IG_DID="your_device_id" \
  -e INSTAGRAM_USERNAME="your_instagram_username" \
  -e CRAWLER_ARGS="--tags=pole,dance --username=your_instagram_username --limit=20" \
  -v $(pwd)/downloads:/app/downloads \
  pole-crawler-ci
```

This will mount the `downloads` directory from your host machine to `/app/downloads` inside the container, ensuring that all downloaded images are persisted on your host system.

### Example Usage:

```bash
# Run with basic arguments (images stored in container only)
docker run \
  -e INSTAGRAM_CSRFTOKEN="your_csrf_token" \
  -e INSTAGRAM_SESSIONID="your_session_id" \
  -e INSTAGRAM_DS_USER_ID="your_user_id" \
  -e INSTAGRAM_IG_DID="your_device_id" \
  -e INSTAGRAM_USERNAME="your_instagram_username" \
  -e CRAWLER_ARGS="--tags=pole,dance --username=your_instagram_username --limit=20" \
  pole-crawler-ci
```

### Advanced Usage with Custom Download Directory

You can also override the download directory using the `DOWNLOADS_DIR` environment variable:

```bash
# Run with custom download directory
docker run \
  -e INSTAGRAM_CSRFTOKEN="your_csrf_token" \
  -e INSTAGRAM_SESSIONID="your_session_id" \
  -e INSTAGRAM_DS_USER_ID="your_user_id" \
  -e INSTAGRAM_IG_DID="your_device_id" \
  -e INSTAGRAM_USERNAME="your_instagram_username" \
  -e DOWNLOADS_DIR="/custom/path/for/downloads" \
  -e CRAWLER_ARGS="--tags=pole,dance --username=your_instagram_username --limit=20" \
  -v $(pwd)/custom-downloads:/custom/path/for/downloads \
  pole-crawler-ci
```

### Required Arguments for main.py:
- `--tags` (required): Comma-separated list of hashtags to search
- `--username` (required): Instagram username
- `--session-path` (optional): Path to session file
- `--sort` (optional): Sort order ("recent" or "top", default: "recent")
- `--limit` (optional): Number of videos to download (default: 10)

## Building the Image

```bash
docker build -t pole-crawler-ci -f ci/Dockerfile .
```