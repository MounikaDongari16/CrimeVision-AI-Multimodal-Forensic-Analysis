# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently, no authentication is required. For production use, implement JWT or OAuth2.

---

## Upload Endpoints

### Upload Single File
Upload a single evidence file.

**Endpoint**: `POST /upload/file`

**Request**:
- Content-Type: `multipart/form-data`
- Body:
  - `file`: File to upload (required)
  - `case_id`: Case identifier (optional, generated if not provided)

**Response**:
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "case_id": "abc123",
  "file_info": {
    "filename": "evidence.jpg",
    "size": 1024000,
    "type": "image",
    "path": "/path/to/file"
  }
}
```

### Upload Multiple Files
Upload multiple evidence files at once.

**Endpoint**: `POST /upload/batch`

**Request**:
- Content-Type: `multipart/form-data`
- Body:
  - `files`: Multiple files (required)
  - `case_id`: Case identifier (optional)

**Response**:
```json
{
  "success": true,
  "message": "Uploaded 3 files",
  "case_id": "abc123",
  "uploaded_files": [...],
  "failed_files": []
}
```

---

## Processing Endpoints

### Process Vision Data
Process all images and videos for a case.

**Endpoint**: `POST /process/vision/{case_id}`

**Response**:
```json
{
  "success": true,
  "case_id": "abc123",
  "total_processed": 5,
  "results": [
    {
      "image_path": "/path/to/image.jpg",
      "detections": [
        {
          "label": "person",
          "confidence": 0.95,
          "bbox": {"x1": 100, "y1": 200, "x2": 300, "y2": 400}
        }
      ]
    }
  ]
}
```

### Process Audio Data
Transcribe and extract facts from audio files.

**Endpoint**: `POST /process/audio/{case_id}`

**Response**:
```json
{
  "success": true,
  "case_id": "abc123",
  "total_processed": 2,
  "results": [
    {
      "audio_path": "/path/to/audio.wav",
      "transcription": {...},
      "facts": {
        "times": ["3:00 PM"],
        "locations": ["Main Street"],
        "actions": ["witnessed incident"]
      }
    }
  ]
}
```

### Process Text Data
Extract entities from police reports.

**Endpoint**: `POST /process/text/{case_id}`

**Response**:
```json
{
  "success": true,
  "case_id": "abc123",
  "total_processed": 1,
  "results": [
    {
      "file_path": "/path/to/report.pdf",
      "entities": {
        "persons": ["John Doe"],
        "locations": ["Main Street"],
        "evidence": ["weapon found"]
      }
    }
  ]
}
```

### Multimodal Fusion
Combine results from all modalities.

**Endpoint**: `POST /process/fusion/{case_id}`

**Request Body**:
```json
{
  "vision_results": [...],
  "audio_results": [...],
  "text_results": [...]
}
```

**Response**:
```json
{
  "success": true,
  "case_id": "abc123",
  "results": {
    "unified_entities": {...},
    "consistency": {...},
    "confidence": 0.85
  }
}
```

### Generate Timeline
Create chronological event timeline.

**Endpoint**: `POST /process/timeline/{case_id}`

**Request Body**:
```json
{
  "vision_results": [...],
  "audio_results": [...],
  "text_results": [...],
  "fusion_results": {...}
}
```

**Response**:
```json
{
  "success": true,
  "case_id": "abc123",
  "timeline": {
    "events": [
      {
        "timestamp": 120.5,
        "source": "vision",
        "description": "Detected 2 persons",
        "confidence": 0.9
      }
    ],
    "total_events": 10
  }
}
```

### 3D Scene Reconstruction
Generate 3D spatial scene.

**Endpoint**: `POST /process/reconstruct/{case_id}`

**Request Body**:
```json
{
  "vision_results": [...],
  "fusion_results": {...}
}
```

**Response**:
```json
{
  "success": true,
  "case_id": "abc123",
  "reconstruction": {
    "scene_data": {...},
    "output_path": "/path/to/scene.json"
  }
}
```

### Generate Report
Create comprehensive evidence report.

**Endpoint**: `POST /process/report/{case_id}`

**Request Body**:
```json
{
  "vision_results": [...],
  "audio_results": [...],
  "text_results": [...],
  "fusion_results": {...},
  "timeline_results": {...},
  "reconstruction_results": {...}
}
```

**Response**:
```json
{
  "success": true,
  "case_id": "abc123",
  "report": {
    "json_report": "/path/to/report.json",
    "pdf_report": "/path/to/report.pdf"
  }
}
```

### Complete Pipeline
Run entire processing pipeline.

**Endpoint**: `POST /process/complete/{case_id}`

**Response**: Returns all processing results in a single response.

---

## Results Endpoints

### Get 3D Scene Data
Retrieve 3D scene JSON data.

**Endpoint**: `GET /results/scene/{case_id}`

**Response**:
```json
{
  "success": true,
  "case_id": "abc123",
  "scene_data": {
    "room": {...},
    "objects": [...]
  }
}
```

### Download JSON Report
Download JSON evidence report.

**Endpoint**: `GET /results/report/json/{case_id}`

**Response**: JSON file download

### Download PDF Report
Download PDF evidence report.

**Endpoint**: `GET /results/report/pdf/{case_id}`

**Response**: PDF file download

### Get Case Summary
Get summary of available results.

**Endpoint**: `GET /results/summary/{case_id}`

**Response**:
```json
{
  "success": true,
  "summary": {
    "case_id": "abc123",
    "available_results": {
      "json_report": true,
      "pdf_report": true,
      "scene_data": true
    },
    "download_links": {...}
  }
}
```

---

## Error Responses

All endpoints return error responses in this format:

```json
{
  "success": false,
  "message": "Error description"
}
```

**Common HTTP Status Codes**:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `413`: File Too Large
- `500`: Internal Server Error

---

## Rate Limiting
Currently no rate limiting. Implement in production.

## CORS
Configured for `localhost:3000`. Update in `config.py` for production.
