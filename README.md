# CrimeVision AI – Intelligent Multimodal Forensic Analysis Platform

A production-ready full-stack application that reconstructs crime scenes in interactive 3D by analyzing images, videos, audio statements, and written reports using state-of-the-art AI models.

## 🎯 Features

- **Multimodal Evidence Processing**: Analyze images, videos, audio, and text documents
- **AI-Powered Analysis**:
  - Object detection with **YOLO** in the initial implementation
  - Upgraded object detection pipeline using **RT-DETR**
  - Image segmentation with SAM
  - Vision-language matching with CLIP
  - Speech-to-text with Whisper
  - Entity extraction from reports
  - Cross-modal fusion with LLaVA
- **Interactive 3D Reconstruction**: Visualize crime scenes in Three.js
- **Timeline Generation**: Chronological event reconstruction
- **Comprehensive Reports**: Generate PDF and JSON evidence reports

## 🧠 Object Detection Model Evolution

The object detection component was developed in two stages.

Initially, the project used **YOLO** for object detection and experimentation. During further development, the detection pipeline was upgraded to **RT-DETR**.

```text
YOLO
  ↓
Initial Object Detection Pipeline
  ↓
Model Evaluation & Development
  ↓
RT-DETR
  ↓
Updated Object Detection Pipeline

📁 Project Structure
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
🚀 Quick Start
Prerequisites
Python 3.8+
Node.js (for serving frontend)
CUDA-capable GPU (recommended, but CPU works)
Backend Setup
Install Python dependencies:
cd backend
pip install -r requirements.txt
Download required models:

Models will be automatically downloaded from HuggingFace on first use.

Ensure you have sufficient disk space for the required models.

Start the backend server:
python app.py

The backend will run on:

http://localhost:5000
Frontend Setup
Serve the frontend:
cd frontend
python -m http.server 3000

Or use Node.js:

npx http-server -p 3000
Open in browser:
http://localhost:3000
📖 Usage
1. Upload Evidence

Drag and drop files into the upload zone.

Supported formats:

Images: JPG, PNG
Videos: MP4, AVI, MOV
Audio: WAV, MP3
Reports: PDF, TXT, DOCX
2. Process Data

Click Start Processing to run the AI pipeline.

The system will:

Detect objects in images/videos
Transcribe audio statements
Extract entities from reports
Fuse multimodal data
Generate timeline
Reconstruct 3D scene
Create evidence reports
3. Review Results
3D Scene: Interact with the reconstructed crime scene
Timeline: View chronological events
Evidence Panel: Browse detections, facts, and entities
Reports: Download JSON or PDF reports
🔧 Configuration

Edit backend/config.py to customize:

Model selection and parameters
File size limits
Processing settings
3D reconstruction parameters
API settings
🧠 AI Models Used
Model	Purpose	Source / Framework
YOLO	Initial object detection implementation	YOLO
RT-DETR	Current object detection pipeline	HuggingFace
SAM	Segmentation	Facebook Research
CLIP	Vision-Language Matching	OpenAI
Whisper	Speech-to-Text	OpenAI
LLaMA/GPT	Text Processing	Meta/OpenAI
LLaVA	Multimodal Fusion	HuggingFace
📊 API Endpoints
Upload
POST /api/upload/file - Upload single file
POST /api/upload/batch - Upload multiple files
GET /api/upload/status/<case_id> - Get upload status
Processing
POST /api/process/vision/<case_id> - Process images/videos
POST /api/process/audio/<case_id> - Process audio files
POST /api/process/text/<case_id> - Process reports
POST /api/process/fusion/<case_id> - Multimodal fusion
POST /api/process/timeline/<case_id> - Generate timeline
POST /api/process/reconstruct/<case_id> - 3D reconstruction
POST /api/process/complete/<case_id> - Run full pipeline
Results
GET /api/results/scene/<case_id> - Get 3D scene data
GET /api/results/report/json/<case_id> - Download JSON report
GET /api/results/report/pdf/<case_id> - Download PDF report
GET /api/results/summary/<case_id> - Get case summary
🎨 Frontend Components
Upload Panel: Drag-and-drop file upload with validation
3D Scene Viewer: Three.js-based interactive visualization
Timeline: Chronological event display with confidence scores
Evidence Panel: Tabbed view of detections, facts, and entities
Status Dashboard: Real-time processing status
⚙️ System Requirements
Minimum
CPU: 4 cores
RAM: 8GB
Storage: 20GB
Recommended
CPU: 8+ cores
RAM: 16GB+
GPU: NVIDIA with 8GB+ VRAM
Storage: 50GB+
🔒 Security Considerations
File validation and size limits
Secure file storage with unique identifiers
No external data transmission (local processing)
Input sanitization
CORS configuration
🐛 Troubleshooting
Models not loading
Ensure internet connection for first-time model download
Check disk space
Verify HuggingFace access
Out of memory errors
Reduce batch size in config.py
Use smaller models where applicable
Process fewer files at once
Frontend not connecting to backend
Verify backend is running on port 5000
Check CORS settings in config.py
Update API_BASE_URL in frontend/js/api.js if needed
📝 License

This project is for educational and research purposes. Ensure compliance with model licenses and local regulations when using for forensic investigations.

🤝 Contributing

This is a demonstration system. For production use:

Add authentication and authorization
Implement database for persistent storage
Add comprehensive error handling
Implement background job queue
Add unit and integration tests
Enhance security measures
👩‍💻 Author

Mounika Dongari

Generative AI Engineer | AI/ML | Computer Vision | Data Science

Areas of Interest
Generative AI
Large Language Models
Multimodal AI
Computer Vision
RAG
Agentic AI
Machine Learning
AI Engineering
Cloud AI
🔑 Technologies
Python YOLO RT-DETR OpenCV PyTorch SAM CLIP Whisper LLaVA LLMs Multimodal AI Computer Vision Deep Learning Flask
