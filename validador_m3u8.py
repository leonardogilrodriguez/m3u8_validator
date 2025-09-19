import requests
import time
import m3u8
from urllib.parse import urljoin

def get_playlist_info(url):
    """
    Gets detailed information from an M3U8 playlist.

    This function performs several checks to ensure the playlist is valid and playable:
    - Loads the playlist and checks if it's a master playlist (with variants).
    - If it's a master playlist, it recursively checks the first variant.
    - Verifies that the playlist contains segments (.ts files).
    - Checks the accessibility of the first two segments to ensure the stream is not broken.
    - Extracts useful metadata (version, bandwidth, codecs, duration, segment count).

    These checks are necessary because:
    - Some M3U8 URLs point to master playlists, not media playlists.
    - A playlist might exist but have no segments (broken or empty).
    - Segments might be listed but not actually accessible (server errors, geo-blocks, etc.).
    - Metadata helps diagnose stream quality and compatibility.
    """
    try:
        # Load the M3U8 file from the given URL
        playlist = m3u8.load(url)

        if playlist.is_variant:
            # If it's a master playlist, select the first variant for validation.
            # This is important because master playlists do not contain media segments directly.
            first_variant = playlist.playlists[0]
            base_uri = url.rsplit('/', 1)[0] + '/'
            variant_url = urljoin(base_uri, first_variant.uri)
            return get_playlist_info(variant_url)  # Recursively check the variant

        if not playlist.segments:
            # If there are no segments, the stream is not playable.
            return {"url": url, "valid": False, "reason": "No .ts segments found"}

        # Check the accessibility of the first two segments.
        # This helps detect streams that are listed but not actually available.
        for i, segment in enumerate(playlist.segments):
            if i >= 2:  # Limit to the first 2 segments for speed
                break
            seg_url = urljoin(playlist.base_uri, segment.uri)
            seg_response = requests.head(seg_url, timeout=10, allow_redirects=True)
            if seg_response.status_code != 200:
                # If a segment is not accessible, the stream is considered broken.
                return {
                    "url": url,
                    "valid": False,
                    "reason": f"Invalid segment: {seg_url} - {seg_response.status_code}"
                }

        # Extract metadata for diagnostics and reporting
        codecs = playlist.media_sequence and playlist.segments[0].program_date_time
        first_segment = playlist.segments[0]
        bandwidth = first_segment.stream_info.bandwidth if hasattr(first_segment, 'stream_info') else None
        codecs = first_segment.stream_info.codecs if hasattr(first_segment, 'stream_info') else None
        duration = sum(seg.duration for seg in playlist.segments)
        version = playlist.version

        return {
            "url": url,
            "valid": True,
            "version": version,
            "bandwidth": bandwidth,
            "codecs": codecs,
            "duration": duration,
            "segments_count": len(playlist.segments),
        }

    except Exception as e:
        # Catch any unexpected errors and report them
        return {"url": url, "valid": False, "reason": str(e)}


def check_headers(url):
    """
    Checks important HTTP headers for the M3U8 URL.

    This function verifies:
    - The Content-Type header to ensure the server is serving the correct MIME type.
    - The presence of CORS headers, which are important for web-based players.
    - The server type for diagnostics.

    These checks are necessary because:
    - Some servers misconfigure MIME types, causing playback issues.
    - Missing CORS headers can prevent playback in browsers.
    - Server information can help with troubleshooting.
    """
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        content_type = response.headers.get("Content-Type", "").lower()
        server = response.headers.get("Server", "")
        cors = response.headers.get("Access-Control-Allow-Origin")

        # Validate that the content type is correct for M3U8 playlists
        valid_content_type = "application/vnd.apple.mpegurl" in content_type or ".m3u8" in url
        # Check if CORS is enabled
        valid_cors = cors is not None

        return {
            "url": url,
            "valid": valid_content_type,
            "content_type": content_type,
            "server": server,
            "cors": cors,
            "valid_content_type": valid_content_type,
            "valid_cors": valid_cors,
        }
    except Exception as e:
        # Return error details if the request fails
        return {"url": url, "valid": False, "error": str(e)}


def check_channel(m3u8_url):
    """
    Performs a full validation of an M3U8 channel URL.

    Steps:
    1. Checks HTTP headers for correct content type and CORS.
    2. Validates the playlist and its segments for accessibility.
    3. Measures load time if the playlist is valid.

    These steps are necessary to ensure:
    - The URL is properly served and accessible.
    - The playlist is not empty or broken.
    - The stream is responsive and not too slow to load.
    """
    try:
        # 1. Check headers for basic accessibility and correctness
        header_result = check_headers(m3u8_url.strip())
        if not header_result["valid"]:
            # If headers are not valid, no need to continue
            return m3u8_url, 0, False, header_result

        # 2. Validate the M3U8 content and its segments
        playlist_info = get_playlist_info(m3u8_url.strip())

        if playlist_info["valid"]:
            # 3. Measure how fast the playlist loads (performance check)
            load_time = measure_load_time(m3u8_url.strip())
            playlist_info["load_time"] = load_time
            return m3u8_url, load_time, True, playlist_info
        else:
            return m3u8_url, 0, False, playlist_info

    except Exception as e:
        # Catch any unexpected errors and report them
        return m3u8_url, 0, False, {"error": str(e)}


def measure_load_time(url):
    """
    Measures the load time of the first KB of the file.

    This is a simple performance check to detect slow or unresponsive streams.
    If the stream is too slow, it may not be suitable for real-time playback.
    """
    try:
        start = time.time()
        with requests.get(url, stream=True, timeout=10) as r:
            r.raise_for_status()
            next(r.iter_content(1024))  # Read only 1KB
        return round(time.time() - start, 2)
    except:
        # If the request fails or is too slow, return infinity
        return float('inf')