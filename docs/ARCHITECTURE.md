# System Architecture

## Overview

The Multimodal AI Crime Scene Reconstruction System is a full-stack application that processes multiple types of evidence (images, videos, audio, text) to generate an interactive 3D crime scene reconstruction with comprehensive analysis.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Browser)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Upload  │  │   3D     │  │ Timeline │  │ Evidence │   │
│  │  Panel   │  │  Scene   │  │  Viewer  │  │  Panel   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                           │                                  │
│                      API Client (api.js)                     │
└───────────────────────────┼──────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Backend (Python)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   API Routes                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │  Upload  │  │Processing│  │ Results  │           │  │
│  │  │  Routes  │  │  Routes  │  │  Routes  │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Service Layer                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │  Vision  │  │  Audio   │  │   Text   │           │  │
│  │  │ Service  │  │ Service  │  │ Service  │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │  Fusion  │  │ Timeline │  │   3D     │           │  │
│  │  │ Service  │  │ Service  │  │Reconstruct│          │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  │  ┌──────────┐                                        │  │
│  │  │  Report  │                                        │  │
│  │  │ Service  │                                        │  │
│  │  └──────────┘                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   AI Models                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │ RT-DETR  │  │  Whisper │  │  LLaVA   │           │  │
│  │  │   CLIP   │  │   LLM    │  │  Open3D  │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      File System                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Uploads  │  │Annotations│ │   3D     │  │ Reports  │   │
│  │  /data   │  │   /data   │ │  Scenes  │  │  /data   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Upload Phase
```
User → Upload Panel → API Client → Upload Routes → File Handler → File System
```

### 2. Processing Phase
```
Processing Routes → Vision Service → RT-DETR/CLIP → Detections
                  → Audio Service → Whisper → Transcription
                  → Text Service → LLM → Entities
                  → Fusion Service → LLaVA → Unified Understanding
                  → Timeline Service → Chronological Events
                  → 3D Service → Open3D → Scene Data
                  → Report Service → ReportLab → PDF/JSON
```

### 3. Visualization Phase
```
Results Routes → API Client → 3D Viewer (Three.js)
                            → Timeline Component
                            → Evidence Panel
```

## Component Descriptions

### Frontend Components

#### Upload Panel
- **Purpose**: File upload interface
- **Technology**: HTML5 File API, Drag & Drop API
- **Features**: Multi-file upload, validation, progress tracking

#### 3D Scene Viewer
- **Purpose**: Interactive 3D visualization
- **Technology**: Three.js
- **Features**: Rotation, zoom, object selection, layer toggling

#### Timeline Viewer
- **Purpose**: Chronological event display
- **Technology**: Custom JavaScript
- **Features**: Event filtering, confidence indicators, source tracking

#### Evidence Panel
- **Purpose**: Evidence summary display
- **Technology**: Tabbed interface
- **Features**: Detections, facts, entities organization

### Backend Services

#### Vision Service
- **Models**: RT-DETR, CLIP, SAM
- **Input**: Images, video frames
- **Output**: Object detections, bounding boxes, labels, confidence scores
- **Processing**: Frame extraction, object detection, segmentation

#### Audio Service
- **Models**: Whisper
- **Input**: Audio files (WAV, MP3)
- **Output**: Transcription, extracted facts (time, location, actions)
- **Processing**: Speech-to-text, NLP fact extraction

#### Text Service
- **Models**: LLM (LLaMA/GPT)
- **Input**: PDF, TXT, DOCX reports
- **Output**: Entities (persons, locations, evidence), relationships
- **Processing**: Text extraction, entity recognition, relationship mapping

#### Fusion Service
- **Models**: LLaVA
- **Input**: Vision, audio, text results
- **Output**: Unified entities, consistency checks, confidence scores
- **Processing**: Cross-modal fusion, consistency validation

#### Timeline Service
- **Input**: All processing results
- **Output**: Chronological event list with uncertainty markers
- **Processing**: Event extraction, temporal ordering, uncertainty quantification

#### 3D Reconstruction Service
- **Models**: Open3D
- **Input**: Vision results, fusion results
- **Output**: 3D scene JSON, PLY visualization
- **Processing**: Spatial positioning, room layout estimation, object placement

#### Report Service
- **Models**: ReportLab
- **Input**: All processing results
- **Output**: PDF and JSON reports
- **Processing**: Data compilation, formatting, PDF generation

## Technology Stack

### Backend
- **Framework**: Flask 3.0
- **Language**: Python 3.8+
- **AI/ML**: PyTorch, Transformers, Whisper, Open3D
- **Document Processing**: PyPDF2, python-docx
- **Report Generation**: ReportLab

### Frontend
- **Core**: HTML5, CSS3, JavaScript (ES6+)
- **3D Graphics**: Three.js
- **Styling**: Custom CSS with CSS Grid and Flexbox
- **API Communication**: Fetch API

### Storage
- **File System**: Local storage for uploads and outputs
- **Format**: JSON for structured data, PLY for 3D meshes

## Security Considerations

1. **File Validation**: Extension and size checks
2. **Secure Storage**: Unique identifiers, isolated directories
3. **Input Sanitization**: Filename sanitization, path validation
4. **CORS**: Configured for specific origins
5. **Error Handling**: No sensitive information in error messages

## Scalability Considerations

### Current Limitations
- Single-threaded processing
- In-memory model loading
- No job queue
- No database

### Production Recommendations
1. **Background Jobs**: Implement Celery or RQ for async processing
2. **Database**: Add PostgreSQL for metadata and results
3. **Caching**: Redis for model caching and session management
4. **Load Balancing**: Multiple backend instances
5. **Storage**: S3 or similar for file storage
6. **GPU Scaling**: Multiple GPU workers for parallel processing

## Performance Optimization

1. **Model Caching**: Models loaded once and reused
2. **Lazy Loading**: Models loaded on-demand
3. **Batch Processing**: Process multiple files together
4. **Frame Sampling**: Extract video frames at intervals
5. **Result Caching**: Store intermediate results

## Deployment Architecture (Production)

```
┌─────────────┐
│   Nginx     │ (Reverse Proxy, Static Files)
└──────┬──────┘
       │
┌──────▼──────┐
│   Gunicorn  │ (WSGI Server)
└──────┬──────┘
       │
┌──────▼──────┐
│ Flask App   │ (Multiple Workers)
└──────┬──────┘
       │
┌──────▼──────┐
│   Celery    │ (Background Jobs)
└──────┬──────┘
       │
┌──────▼──────┐
│  PostgreSQL │ (Database)
│    Redis    │ (Cache/Queue)
│     S3      │ (File Storage)
└─────────────┘
```

## Monitoring and Logging

- **Logging**: Structured logging with timestamps and context
- **Metrics**: Processing time, success rate, model performance
- **Alerts**: Error notifications, resource usage warnings

## Future Enhancements

1. Real-time processing with WebSockets
2. Multi-user support with authentication
3. Advanced 3D features (textures, lighting, shadows)
4. Video playback synchronized with timeline
5. Collaborative annotation tools
6. Export to forensic software formats
7. Mobile application
8. Cloud deployment options
