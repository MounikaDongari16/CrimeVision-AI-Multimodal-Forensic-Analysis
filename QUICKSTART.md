# Quick Start Guide

## 🚀 Running the System

### Step 1: Start Backend

```bash
cd c:\Users\mouni\Documents\crime\backend
pip install -r requirements.txt
python app.py
```

### Step 1.5: Set Up Groq API Key
1. Create a `.env` file in the `backend/` folder.
2. Add: `GROQ_API_KEY=your_key_here`


```bash
cd c:\Users\mouni\Documents\crime\frontend
python -m http.server 3000
```

✅ Frontend running on `http://localhost:3000`

### Step 3: Open Browser

Navigate to: `http://localhost:3000`

---

## 📤 Using the System

### 1. Upload Files
- Drag and drop evidence files into the upload zone
- Supported: Images (JPG, PNG), Videos (MP4), Audio (WAV, MP3), Reports (PDF, TXT)

### 2. Start Processing
- Click "🚀 Start Processing" button
- Wait for AI pipeline to complete (30 seconds - 5 minutes depending on files)

### 3. Review Results
- **3D Scene**: Interactive 3D reconstruction
- **Timeline**: Chronological events
- **Evidence Panel**: Detections, facts, entities

### 4. Download Reports
- Click "📄 Download JSON" for structured data
- Click "📕 Download PDF" for formatted report

---

## 🎯 Example Test Case

Create a test case with:
- 2-3 images (crime scene photos)
- 1 short video (10-30 seconds)
- 1 audio file (witness statement)
- 1 text report (police report)

The system will:
✅ Detect objects in images/videos
✅ Transcribe audio and extract facts
✅ Extract entities from reports
✅ Fuse all information
✅ Generate timeline
✅ Create 3D scene
✅ Produce comprehensive report

---

## 🔧 Troubleshooting

### Backend won't start
- Check Python version (3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 5000 is available

### Frontend won't connect
- Verify backend is running
- Check browser console for errors
- Update API_BASE_URL in `frontend/js/api.js` if needed

### Models not loading
- First run will download models (requires internet)
- Ensure sufficient disk space (~10GB)
- Check HuggingFace access

### Out of memory
- Reduce batch size in `backend/config.py`
- Use smaller Whisper model ('base' instead of 'large')
- Process fewer files at once

---

## 📚 Documentation

- **README.md**: Full project documentation
- **docs/API.md**: API reference
- **docs/ARCHITECTURE.md**: System architecture
- **data/sample_structure.md**: Dataset guidelines
- **walkthrough.md**: Feature walkthrough

---

## 🎨 Key Features

✅ **Multimodal AI Processing**: Images, videos, audio, text
✅ **Object Detection**: RT-DETR for people, weapons, vehicles
✅ **Speech-to-Text**: Whisper transcription
✅ **Entity Extraction**: NLP for reports
✅ **Multimodal Fusion**: Cross-modal consistency
✅ **Timeline Generation**: Chronological reconstruction
✅ **3D Visualization**: Interactive Three.js scene
✅ **Report Generation**: PDF and JSON outputs

---

## 🏗️ Project Structure

```
crime/
├── backend/          # Flask API + AI services
├── frontend/         # HTML/CSS/JS dashboard
├── data/            # Uploads and outputs
└── docs/            # Documentation
```

---

## 🤝 Support

For issues or questions, refer to:
- README.md for setup instructions
- API.md for endpoint documentation
- ARCHITECTURE.md for system design
- walkthrough.md for feature details

---

**Ready to use!** 🎉
