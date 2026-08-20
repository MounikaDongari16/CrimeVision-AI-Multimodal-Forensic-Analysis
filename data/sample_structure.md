# Sample Dataset Structure

This document describes the organization of sample data for testing the Crime Scene Reconstruction System.

## Directory Structure

```
data/
├── uploads/                    # Uploaded evidence files
│   └── {case_id}/             # Per-case directories
│       ├── images/            # Crime scene photos
│       ├── videos/            # CCTV footage
│       ├── audio/             # Witness statements
│       └── reports/           # Police reports
│
├── outputs/                   # Processing results
│   ├── annotations/           # Annotated images/videos
│   │   └── {case_id}/
│   │       ├── image_001_annotated.jpg
│   │       └── video_001_frame_0001.jpg
│   │
│   ├── reconstructions/       # 3D scene data
│   │   └── {case_id}/
│   │       ├── scene.json
│   │       └── scene_visualization.ply
│   │
│   ├── reports/               # Generated reports
│   │   └── {case_id}/
│   │       ├── evidence_report.json
│   │       └── evidence_report.pdf
│   │
│   └── temp/                  # Temporary processing files
│       └── {case_id}/
│           └── video_frames/
│
└── samples/                   # Sample test data (optional)
    ├── images/
    │   ├── crime_scene_001.jpg
    │   ├── crime_scene_002.jpg
    │   └── evidence_photo_001.jpg
    │
    ├── videos/
    │   ├── cctv_footage_001.mp4
    │   └── cctv_footage_002.mp4
    │
    ├── audio/
    │   ├── witness_statement_001.wav
    │   └── witness_statement_002.mp3
    │
    └── reports/
        ├── police_report_001.pdf
        └── incident_report_001.txt
```

## Sample Data Guidelines

### Images
- **Format**: JPG, PNG
- **Resolution**: Minimum 640x480, recommended 1920x1080
- **Content**: Crime scene photos, evidence close-ups, location shots
- **Naming**: Descriptive names (e.g., `crime_scene_overview.jpg`, `weapon_closeup.jpg`)

**Example Image Scenarios**:
- Wide shot of crime scene
- Close-up of evidence items
- Suspect or victim photos
- Location landmarks

### Videos
- **Format**: MP4 (H.264 codec recommended)
- **Duration**: 10 seconds to 10 minutes
- **Resolution**: Minimum 640x480, recommended 1280x720
- **Frame Rate**: 24-30 fps
- **Content**: CCTV footage, dashcam recordings, witness videos

**Example Video Scenarios**:
- CCTV footage showing suspect
- Dashcam recording of incident
- Security camera footage
- Witness-recorded video

### Audio
- **Format**: WAV (preferred) or MP3
- **Duration**: 30 seconds to 5 minutes
- **Quality**: 16-bit, 44.1kHz minimum
- **Content**: Witness statements, 911 calls, interviews

**Example Audio Content**:
```
"I was walking down Main Street around 3 PM when I heard a loud noise. 
I saw a man wearing a black jacket running from the building. 
He got into a red car parked on the corner and drove away quickly."
```

### Reports
- **Format**: PDF, TXT, DOCX
- **Length**: 1-10 pages
- **Content**: Police reports, incident descriptions, witness statements

**Example Report Structure**:
```
INCIDENT REPORT

Case Number: 2024-001
Date: January 20, 2024
Time: 15:30
Location: 123 Main Street

Description:
Witness John Doe reported seeing a suspicious individual near the 
location at approximately 3:00 PM. The suspect was described as a 
male, approximately 6 feet tall, wearing dark clothing. A weapon 
was recovered at the scene.

Evidence:
- Weapon (knife) found at scene
- CCTV footage from nearby camera
- Witness statement from John Doe
- Fingerprints collected

Officers:
- Officer Jane Smith (Badge #1234)
- Officer Bob Johnson (Badge #5678)
```

## Creating Test Data

### Option 1: Use Public Datasets
- **COCO Dataset**: For object detection testing
- **UrbanSound8K**: For audio classification
- **Sample Documents**: Create fictional police reports

### Option 2: Generate Synthetic Data
- Use image generation tools for crime scene mockups
- Record sample witness statements
- Create fictional police reports

### Option 3: Use Provided Samples
The system includes placeholder support for:
- Sample images with common objects (people, vehicles, bags)
- Sample audio with clear speech
- Sample text reports with structured information

## Data Privacy and Ethics

⚠️ **IMPORTANT**: 
- Never use real crime scene data without proper authorization
- Ensure all test data is fictional or properly licensed
- Respect privacy laws and regulations
- Obtain consent for any real audio/video recordings
- This system is for educational and research purposes

## Testing Scenarios

### Scenario 1: Simple Detection
- **Files**: 2-3 images with people and objects
- **Expected**: Object detection, bounding boxes
- **Purpose**: Test vision service

### Scenario 2: Timeline Reconstruction
- **Files**: 1 video (30 seconds), 1 audio statement
- **Expected**: Chronological timeline with events
- **Purpose**: Test timeline generation

### Scenario 3: Multimodal Fusion
- **Files**: 2 images, 1 audio, 1 report
- **Expected**: Cross-modal entity matching
- **Purpose**: Test fusion service

### Scenario 4: Complete Pipeline
- **Files**: 3 images, 1 video, 2 audio files, 1 report
- **Expected**: Full 3D reconstruction, timeline, report
- **Purpose**: End-to-end system test

## File Size Recommendations

- **Images**: 500KB - 5MB each
- **Videos**: 5MB - 50MB each
- **Audio**: 500KB - 10MB each
- **Reports**: 100KB - 5MB each
- **Total per case**: < 200MB recommended

## Metadata Format

Each case can include a `metadata.json` file:

```json
{
  "case_id": "test_case_001",
  "created_at": "2024-01-20T15:30:00Z",
  "description": "Test case for system validation",
  "files": {
    "images": 3,
    "videos": 1,
    "audio": 2,
    "reports": 1
  },
  "expected_results": {
    "detections": ["person", "vehicle", "weapon"],
    "locations": ["Main Street"],
    "timeline_events": 5
  }
}
```

## Validation Checklist

Before testing:
- [ ] All files are in correct formats
- [ ] File sizes are within limits
- [ ] Images contain detectable objects
- [ ] Audio has clear speech
- [ ] Reports contain structured information
- [ ] No sensitive or real crime data is used
- [ ] Files are organized in correct directories

## Sample Data Sources

**Free Resources**:
- Pexels / Unsplash: Free stock photos
- Pixabay: Free videos
- Freesound: Free audio samples
- Lorem Ipsum generators: Sample text

**Synthetic Data**:
- Generate with AI image tools (ensure license compliance)
- Record your own audio statements
- Write fictional reports

---

**Note**: The system will create the necessary directories automatically when processing files. You only need to prepare the sample data.
