# How to Run CrimeVision AI – Intelligent Multimodal Forensic Analysis Platform

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ Internet connection (for downloading AI models on first run)
- ✅ At least 10GB free disk space

---

## 🚀 Step-by-Step Instructions

### Step 1: Install Python Dependencies

Open a **new terminal/command prompt** and run:

```bash
cd c:\Users\mouni\Documents\crime\backend
pip install -r requirements.txt
```

**Wait time**: 5-10 minutes (depending on your internet speed)

**What this does**: Installs all required Python libraries (Flask, PyTorch, Transformers, etc.)

### Step 1.5: Set Up Groq API Key

The system uses Groq for advanced AI summaries and chat. 
1. Create a `.env` file in the `backend/` folder.
2. Add your Groq API key:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```

---

### Step 2: Start the Backend Server

In the **same terminal**, run:

```bash
python app.py
```

**Expected output**:
```
2026-01-23 10:33:48,612 - flask_app - INFO - Initializing Crime Scene Reconstruction System
2026-01-23 10:33:48,612 - flask_app - INFO - Application initialized successfully
2026-01-23 10:33:48,612 - flask_app - INFO - Starting server on 0.0.0.0:5000
 * Running on http://0.0.0.0:5000
 * Debugger is active!
```

✅ **Backend is now running!** Keep this terminal open.

---

### Step 3: Start the Frontend Server

Open a **new terminal/command prompt** (keep the backend terminal running) and run:

```bash
cd c:\Users\mouni\Documents\crime\frontend
python -m http.server 3000
```

**Expected output**:
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

✅ **Frontend is now running!** Keep this terminal open too.

---

### Step 4: Open the Application in Browser

1. Open your web browser (Chrome, Firefox, or Edge)
2. Navigate to: **http://localhost:3000**
3. You should see the CrimeVision AI dashboard

---

## 🎯 Using the Application

### Upload Files

1. **Drag and drop** files into the upload zone, or click to browse
2. Supported file types:
   - **Images**: JPG, PNG (crime scene photos)
   - **Videos**: MP4, AVI, MOV (CCTV footage)
   - **Audio**: WAV, MP3 (witness statements)
   - **Reports**: PDF, TXT (police reports)

### Process Evidence

1. After uploading files, click **"🚀 Start Processing"**
2. Wait for the AI pipeline to complete (30 seconds to 5 minutes)
3. Watch the status indicators update:
   - Vision Analysis
   - Audio Transcription
   - Text Processing
   - Multimodal Fusion
   - Timeline Generation
   - 3D Reconstruction
   - Report Generation

### View Results

Once processing is complete:
- **3D Scene**: Interactive 3D reconstruction (rotate with mouse)
- **Timeline**: Chronological events from all evidence
- **Evidence Panel**: Detected objects, facts, and entities
- **Reports**: Download JSON or PDF reports

---

## 📝 Example Test Case

For your first test, try uploading:
- 1-2 images (any photos with people or objects)
- 1 short audio file (or record a simple statement)
- 1 text file with some information

The system will analyze everything and create a 3D reconstruction!

---

## ⚠️ Important Notes

### First Run
- **AI models will download automatically** on first use (~2-5 GB)
- This requires internet connection
- First processing will take longer (5-10 minutes)
- Subsequent runs will be much faster

### System Requirements
- **Minimum**: 8GB RAM, 4-core CPU
- **Recommended**: 16GB RAM, GPU with CUDA support
- **Without GPU**: Processing will be slower but still works

---

## 🔧 Troubleshooting

### Backend won't start
**Problem**: `ModuleNotFoundError` or import errors

**Solution**:
```bash
cd c:\Users\mouni\Documents\crime\backend
pip install -r requirements.txt --upgrade
```

### Port already in use
**Problem**: "Address already in use" error

**Solution**:
- Backend: Change port in `backend/config.py` (line 104)
- Frontend: Use different port: `python -m http.server 8000`

### "Failed to fetch" error in browser
**Problem**: Frontend can't connect to backend

**Solution**:
1. Verify backend is running (check terminal)
2. Refresh browser (F5)
3. Check browser console (F12) for errors

### Out of memory
**Problem**: System crashes during processing

**Solution**:
- Process fewer files at once
- Use smaller AI models (edit `backend/config.py`)
- Close other applications

---

## 🛑 Stopping the Application

To stop the servers:

1. **Backend**: Press `Ctrl+C` in the backend terminal
2. **Frontend**: Press `Ctrl+C` in the frontend terminal

---

## 📚 Additional Resources

- **Full Documentation**: `README.md`
- **API Reference**: `docs/API.md`
- **System Architecture**: `docs/ARCHITECTURE.md`
- **Feature Walkthrough**: See artifacts in `.gemini/antigravity/brain/`

---

## ✅ Quick Checklist

Before running:
- [ ] Python 3.8+ installed
- [ ] Internet connection available
- [ ] 10GB+ free disk space

Running:
- [ ] Backend terminal open and running
- [ ] Frontend terminal open and running
- [ ] Browser open at http://localhost:3000

Ready to process:
- [ ] Files uploaded
- [ ] "Start Processing" button clicked
- [ ] Watching the magic happen! 🎉

---

**Need Help?** Check the troubleshooting section above or review the documentation files.
