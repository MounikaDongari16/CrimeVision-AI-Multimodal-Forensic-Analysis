/**
 * Main Application Logic
 */

// Initialize components
let currentCaseId = null;
let processingResults = {};

const uploadPanel = new UploadPanel();
const scene3D = new Scene3D('sceneContainer');
const timeline = new Timeline('timelineContainer');
const evidencePanel = new EvidencePanel();

// New Case Button
document.getElementById('newCaseBtn').addEventListener('click', () => {
    if (confirm('Start a new case? This will clear current data.')) {
        resetApplication();
    }
});

// Process Button
document.getElementById('processBtn').addEventListener('click', async () => {
    await startProcessing();
});

// Download Buttons
document.getElementById('downloadJsonBtn').addEventListener('click', () => {
    if (currentCaseId) {
        window.open(API.getJsonReportUrl(currentCaseId), '_blank');
    }
});

document.getElementById('downloadPdfBtn').addEventListener('click', () => {
    if (currentCaseId) {
        window.open(API.getPdfReportUrl(currentCaseId), '_blank');
    }
});

// Scene Controls
document.getElementById('resetViewBtn').addEventListener('click', () => {
    scene3D.resetView();
});

/**
 * Start processing pipeline
 */
async function startProcessing() {
    try {
        const files = uploadPanel.getFiles();

        if (files.length === 0) {
            console.log('No files uploaded');
            return;
        }

        // Disable process button
        const btn = document.getElementById('processBtn');
        btn.disabled = true;

        // Check for Audio-Only flow (Direct Analysis Request)
        const audioFile = files.find(f => f.type.startsWith('audio/'));
        const isAudioOnly = files.length === 1 && audioFile;

        if (isAudioOnly) {
            btn.textContent = '⏳ Processing audio...';
            updateStatus('Audio upload detected. Starting direct analysis...', 'processing');

            // Show Blue Box Loader
            const blueBox = document.getElementById('blueBox');
            blueBox.style.display = 'block';
            blueBox.innerHTML = '<strong>Processing audio...</strong> (Reading file & running Whisper-Tiny)';
            blueBox.style.background = '#e3f2fd';
            blueBox.style.color = '#333';

            // Direct Upload using API helper (Handles Base URL)
            const result = await API.analyzeAudio(audioFile);
            console.log("Audio Analysis Result:", result);

            if (result.status === 'success') {
                // UPDATE BLUE BOX
                blueBox.innerHTML = `<strong>Transcript:</strong><br>${result.transcript}`;
                blueBox.style.background = '#e3f2fd'; // Keep it Blue
                blueBox.style.border = '1px solid #b6d4fe';

                // Also update the main evidence panel for consistent UI
                if (result.translations) {
                    evidencePanel.updateAudioFindings([{
                        transcription: { english: result.transcript },
                        translations: result.translations,
                        summary: result.one_line_summary,
                        crime_analysis: result.crime_analysis,
                        timeline: result.timeline
                    }]);
                }
                updateStatus('Audio analysis complete!', 'complete');
            } else {
                throw new Error(result.message || 'Unknown error');
            }

            btn.disabled = false;
            btn.textContent = '🚀 Start Processing';
            return; // Exit early, skipping the complex pipeline
        }

        // --- ORIGINAL PIPELINE (Images/Video/Batch) ---
        btn.textContent = '⏳ Processing batch...';

        // Upload files
        updateStatus('Uploading files...', 'processing');
        const uploadResult = await API.uploadBatch(files);

        if (!uploadResult.success) {
            throw new Error('Upload failed: ' + uploadResult.message);
        }

        currentCaseId = uploadResult.case_id;
        document.getElementById('currentCaseId').textContent = currentCaseId;

        // Display uploaded images in 3D scene
        scene3D.displayUploadedImages(files);

        // Immediate result handling (Auto-detection results)
        if (uploadResult.uploaded_files && uploadResult.uploaded_files.length > 0) {
            const allDetections = uploadResult.uploaded_files.flatMap(f => f.detections || []);
            if (allDetections.length > 0) {
                evidencePanel.updateDetections(allDetections);

                // Update 3D scene summary 
                const avgConfidence = (allDetections.reduce((sum, det) => sum + det.confidence, 0) / allDetections.length * 100).toFixed(0);
                document.getElementById('objectCount').textContent = allDetections.length;
                document.getElementById('avgConfidence').textContent = avgConfidence + '%';
                updateStatusItem('Vision Analysis', 'complete');

                // Draw detections
                scene3D.drawDetections(allDetections);
            }
        }

        // Run complete pipeline
        updateStatus('Running AI pipeline...', 'processing');
        const result = await API.processCompletePipeline(currentCaseId);

        if (!result.success) {
            throw new Error('Processing failed: ' + result.message);
        }

        // Store results
        processingResults = result;

        // Update UI with results
        await updateUIWithResults(result);

        // Enable download buttons
        document.getElementById('downloadJsonBtn').disabled = false;
        document.getElementById('downloadPdfBtn').disabled = false;

        updateStatus('Processing complete!', 'complete');

    } catch (error) {
        console.error('Processing error:', error);

        // Show error in Blue Box if active
        const blueBox = document.getElementById('blueBox');
        if (blueBox && blueBox.style.display === 'block') {
            blueBox.innerHTML = `<strong>Error:</strong> ${error.message}`;
            blueBox.style.background = '#f8d7da';
            blueBox.style.color = '#721c24';
        }

        updateStatus('Processing failed', 'error');
    } finally {
        document.getElementById('processBtn').disabled = false;
        document.getElementById('processBtn').textContent = '🚀 Start Processing';
    }
}

/**
 * Update UI with processing results
 */
async function updateUIWithResults(results) {
    // Update status indicators
    updateStatusItem('Vision Analysis', 'complete');
    updateStatusItem('Audio Transcription', 'complete');
    updateStatusItem('Text Processing', 'complete');
    updateStatusItem('Multimodal Fusion', 'complete');
    updateStatusItem('Timeline Generation', 'complete');
    updateStatusItem('3D Reconstruction', 'complete');
    updateStatusItem('Report Generation', 'complete');

    // Update 3D scene
    if (results.reconstruction_results && results.reconstruction_results.scene_data) {
        scene3D.loadSceneData(results.reconstruction_results.scene_data);
    }

    // Update timeline
    if (results.timeline_results) {
        timeline.render(results.timeline_results);
    }

    // Update evidence panel
    if (results.vision_results && results.vision_results.length > 0) {
        const allDetections = results.vision_results.flatMap(r => r.detections || []);
        evidencePanel.updateDetections(allDetections);

        // New: Pass vision summary for metrics (People, Weapons, Location)
        if (results.vision_summary) {
            evidencePanel.updateMetrics(results.vision_summary);
        }

        // Draw detections in 3D scene
        scene3D.drawDetections(allDetections);
    }

    if (results.audio_results && results.audio_results.length > 0) {
        // Pass full audio results for multilingual transcription and timeline
        evidencePanel.updateAudioFindings(results.audio_results);
        evidencePanel.updateFacts(results.all_facts || {});
    } else if (results.all_facts) {
        evidencePanel.updateFacts(results.all_facts);
    }

    if (results.fusion_results && results.fusion_results.unified_entities) {
        evidencePanel.updateEntities(results.fusion_results.unified_entities);
    }
}

/**
 * Update processing status
 */
function updateStatus(message, status) {
    console.log(`[${status}] ${message}`);
}

/**
 * Update individual status item
 */
function updateStatusItem(label, status) {
    const statusItems = document.querySelectorAll('.status-item');
    statusItems.forEach(item => {
        const itemLabel = item.querySelector('.status-label').textContent;
        if (itemLabel === label) {
            const badge = item.querySelector('.status-badge');
            badge.className = `status-badge status-${status}`;
            badge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
    });
}

/**
 * Reset application
 */
function resetApplication() {
    currentCaseId = null;
    processingResults = {};

    document.getElementById('currentCaseId').textContent = 'None';

    uploadPanel.clear();
    scene3D.clearScene();
    timeline.clear();

    document.getElementById('downloadJsonBtn').disabled = true;
    document.getElementById('downloadPdfBtn').disabled = true;

    // Reset status items
    const statusItems = document.querySelectorAll('.status-item');
    statusItems.forEach(item => {
        const badge = item.querySelector('.status-badge');
        badge.className = 'status-badge status-pending';
        badge.textContent = 'Pending';
    });
}

// Initialize
console.log('Crime Scene Reconstruction System initialized');
