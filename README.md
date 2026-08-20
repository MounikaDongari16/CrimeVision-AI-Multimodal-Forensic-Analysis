#  CrimeVision AI – Intelligent Multimodal Forensic Analysis Platform
A production-ready full-stack application that reconstructs crime scenes in interactive 3D by analyzing images, videos, audio statements, and written reports using state-of-the-art AI models.
## 🔬 Object Detection

During the development of the project, I experimented with **YOLO** for object detection. As the project evolved, I also explored and integrated **RT-DETR** into the object detection pipeline.

This provided hands-on experience with two different object detection approaches and helped in evaluating the models for the project's multimodal forensic analysis workflow.

**Object Detection Models Explored:**
- YOLO – Initial experimentation and implementation
- RT-DETR – Later integrated into the updated pipeline

## 🎯 Features

- **Multimodal Evidence Processing**: Analyze images, videos, audio, and text documents
- **AI-Powered Analysis**:
  - Object detection using **YOLO** during the initial development and experimentation phase
  - Object detection pipeline later upgraded to **RT-DETR**
  - Image segmentation with SAM
  - Vision-language matching with CLIP
  - Speech-to-text with Whisper
  - Entity extraction from reports
  - Cross-modal fusion with LLaVA
- **Interactive 3D Reconstruction**: Visualize crime scenes in Three.js
- **Timeline Generation**: Chronological event reconstruction
- **Comprehensive Reports**: Generate PDF and JSON evidence reports

## 📁 Project Structure

crime/
├── backend/
│   ├── app.py                 # Flask application
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── services/              # AI processing services
│   │   ├── vision_service.py
│   │   ├── audio_service.py
│   │   ├── text_service.py
│   │   ├── fusion_service.py
│   │   ├── timeline_service.py
│   │   ├── reconstruction_service.py
│   │   └── report_service.py
│   ├── routes/                # API endpoints
│   │   ├── upload_routes.py
│   │   ├── processing_routes.py
│   │   └── results_routes.py
│   └── utils/                 # Utilities
│       ├── logger.py
│       ├── file_handler.py
│       └── model_loader.py
├── frontend/
│   ├── index.html             # Main dashboard
│   ├── css/
│   │   └── styles.css         # Styling
│   └── js/
│       ├── api.js             # API client
│       ├── app.js             # Main application
│       └── components/        # UI components
│           ├── scene3d.js
│           ├── timeline.js
│           ├── upload-panel.js
│           └── evidence-panel.js
├── data/
│   ├── uploads/               # Uploaded files
│   └── outputs/               # Processing results
└── docs/
    ├── API.md                 # API documentation
    └── ARCHITECTURE.md        # System architecture

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for serving frontend)
- CUDA-capable GPU (recommended, but CPU works)

### Backend Setup

1. *Install Python dependencies*:
bash
cd backend
pip install -r requirements.txt


2. *Download required models* (optional - models will download on first use):
bash
# Models will be automatically downloaded from HuggingFace
# Ensure you have sufficient disk space (~10GB)


3. *Start the backend server*:
bash
python app.py


The backend will run on http://localhost:5000

### Frontend Setup

1. *Serve the frontend*:
bash
cd frontend
# Using Python's built-in server
python -m http.server 3000


Or use any static file server:
bash
# Using Node.js http-server
npx http-server -p 3000


2. *Open in browser*:
Navigate to http://localhost:3000

## 📖 Usage

### 1. Upload Evidence

- Drag and drop files into the upload zone
- Supported formats:
  - *Images*: JPG, PNG
  - *Videos*: MP4, AVI, MOV
  - *Audio*: WAV, MP3
  - *Reports*: PDF, TXT, DOCX

### 2. Process Data

- Click "Start Processing" to run the AI pipeline
- The system will:
  1. Detect objects in images/videos
  2. Transcribe audio statements
  3. Extract entities from reports
  4. Fuse multimodal data
  5. Generate timeline
  6. Reconstruct 3D scene
  7. Create evidence reports

### 3. Review Results

- *3D Scene*: Interact with the reconstructed crime scene
- *Timeline*: View chronological events
- *Evidence Panel*: Browse detections, facts, and entities
- *Reports*: Download JSON or PDF reports

## 🔧 Configuration

Edit backend/config.py to customize:

- Model selection and parameters
- File size limits
- Processing settings
- 3D reconstruction parameters
- API settings

## 🧠 AI Models Used

| Model | Purpose | Source |
|-------|---------|--------|
| YOLO | Object Detection | HuggingFace |
| RT-DETR | Object Detection | HuggingFace |
| SAM | Segmentation | Facebook Research |
| CLIP | Vision-Language Matching | OpenAI |
| Whisper | Speech-to-Text | OpenAI |
| LLaMA/GPT | Text Processing | Meta/OpenAI |
| LLaVA | Multimodal Fusion | HuggingFace |

## 📊 API Endpoints

### Upload
- POST /api/upload/file - Upload single file
- POST /api/upload/batch - Upload multiple files
- GET /api/upload/status/<case_id> - Get upload status

### Processing
- POST /api/process/vision/<case_id> - Process images/videos
- POST /api/process/audio/<case_id> - Process audio files
- POST /api/process/text/<case_id> - Process reports
- POST /api/process/fusion/<case_id> - Multimodal fusion
- POST /api/process/timeline/<case_id> - Generate timeline
- POST /api/process/reconstruct/<case_id> - 3D reconstruction
- POST /api/process/complete/<case_id> - Run full pipeline

### Results
- GET /api/results/scene/<case_id> - Get 3D scene data
- GET /api/results/report/json/<case_id> - Download JSON report
- GET /api/results/report/pdf/<case_id> - Download PDF report
- GET /api/results/summary/<case_id> - Get case summary

## 🎨 Frontend Components

- *Upload Panel*: Drag-and-drop file upload with validation
- *3D Scene Viewer*: Three.js-based interactive visualization
- *Timeline*: Chronological event display with confidence scores
- *Evidence Panel*: Tabbed view of detections, facts, and entities
- *Status Dashboard*: Real-time processing status

## ⚙️ System Requirements

### Minimum
- CPU: 4 cores
- RAM: 8GB
- Storage: 20GB

### Recommended
- CPU: 8+ cores
- RAM: 16GB+
- GPU: NVIDIA with 8GB+ VRAM
- Storage: 50GB+

## 🔒 Security Considerations

- File validation and size limits
- Secure file storage with unique identifiers
- No external data transmission (local processing)
- Input sanitization
- CORS configuration

## 🐛 Troubleshooting

### Models not loading
- Ensure internet connection for first-time model download
- Check disk space
- Verify HuggingFace access

### Out of memory errors
- Reduce batch size in config.py
- Use smaller models (e.g., Whisper 'base' instead of 'large')
- Process fewer files at once

### Frontend not connecting to backend
- Verify backend is running on port 5000
- Check CORS settings in config.py
- Update API_BASE_URL in frontend/js/api.js if needed

## 📝 License

This project is for educational and research purposes. Ensure compliance with model licenses and local regulations when using for forensic investigations.

## 🤝 Contributing

This is a demonstration system. For production use:
- Add authentication and authorization
- Implement database for persistent storage
- Add comprehensive error handling
- Implement background job queue
- Add unit and integration tests
- Enhance security measures

## 📧 Support

For issues or questions, please refer to the documentation in the docs/ directory.

---

*Built with*: Python, Flask, Three.js, HuggingFace Transformers, Open3D, Whisper
