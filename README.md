# M3U8 Validator

## Project Motivation
This project aims to explore M3U8 playlist functionality and create a validation tool with a server component to diagnose why an M3U8 file might be invalid. The tool provides both command-line and server-based validation capabilities for developers working with HLS streaming content.

## Components
- **validador_m3u8.py**: Core CLI script for validating M3U8 files
- **server.py**: REST API server to validate playlists via HTTP requests
- **Docker support**: Containerization via Docker and docker-compose for easy deployment

## Features
- Thread-based parallel URL validation
- Output filtering for valid entries
- Server API endpoints for programmatic validation
- Detailed validation reports showing errors
- Dockerized environment for consistent execution

## Installation
Ensure Python 3.8+ is installed. For local use:
```bash
pip install -r requirements.txt
```

## Usage

### Server Mode
Start the validation server:
```bash
python server.py
```
The server listens on `http://localhost:5665` with these endpoints:
- `POST /validateM3U8`: Validate a playlist file upload

Payload example

```javascript
{"url":"https://video.twimg.com/amplify_video/1969034320321929216/pl/RFT633SNhqFz7FSJ.m3u8?variant_version=1&tag=21"}
```

**Example request**:
```bash
curl -X POST http://localhost:5665/validateM3U8   -H "Content-Type: application/json"   -d '{"url":"https://video.twimg.com/amplify_video/1969034320321929216/pl/RFT633SNhqFz7FSJ.m3u8?variant_version=1&tag=21"}'
```

## Docker Deployment
Build and run the container:
```bash
docker-compose up --build
```
Access via `http://localhost:5665`

## Validation Workflow
1. The tool parses the M3U8 file structure
2. Validates playlist syntax and tag compliance
3. Performs HTTP head checks on media URLs
4. Produces filtered output and error diagnostics

## Contributing
This project welcomes contributions. Please:
1. Fork the repository
2. Add tests for new functionality
3. Maintain PEP8 compliance
4. Update documentation as needed

## Architecture Overview
```
+----------------+       +---------------+       +------------+
| CLI/Server API | ----> | Validation    | ----> | Results    |
| (validador.py) |       | Core          |       | Processing |
+----------------+       +---------------+       +------------+
          ^                            |
          | Error/Issue Feedback        |
          +----------------------------+
