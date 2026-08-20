/**
 * Image Analysis Page Logic
 */

// Initialize dedicated components
const uploadPanel = new UploadPanel();
const scene3D = new Scene3D('sceneContainer');
const evidencePanel = new EvidencePanel();
const chatHandler = new ChatHandler('image');

// Protocol Warning Check
if (window.location.protocol === 'file:') {
    console.warn("CRITICAL: Dashboard opened via file:// protocol. PDF downloads and API features may be blocked by browser security. Please use http://localhost:3000/image.html");
}

let currentCaseId = null;

document.getElementById('processBtn').addEventListener('click', async () => {
    await startProcessing();
});

document.getElementById('resetViewBtn').addEventListener('click', () => {
    scene3D.resetView();
});

const downloadBtn = document.getElementById('downloadReportBtn');
let lastAnalysisResult = null;

// Download handler
downloadBtn.addEventListener('click', async () => {
    if (!lastAnalysisResult || !currentCaseId) return;

    downloadBtn.disabled = true;
    downloadBtn.textContent = '⏳ Generating PDF...';

    try {
        const result = await API.generateImageReport(currentCaseId, {
            image_path: lastAnalysisResult.image_path, // Backend needs to persist this or we send it
            // For now, simpler to send the facts we already have
            facts: lastAnalysisResult.facts,
            scenarios: lastAnalysisResult.scenarios
        });

        if (result.success && result.pdf_url) {
            const link = document.createElement('a');
            // Ensure absolute link to backend server to support file:// protocol
            link.href = `http://localhost:5000${result.pdf_url}`;
            link.download = result.filename;
            link.textContent = 'Click here if download didn\'t start';
            link.className = 'btn btn-secondary btn-sm';

            const container = document.getElementById('downloadLinkContainer');
            container.innerHTML = '';
            container.appendChild(link);
            container.style.display = 'block';

            link.click();
            downloadBtn.textContent = '📄 Download PDF Report';
        }
    } catch (error) {
        console.error("PDF Error:", error);
        alert("Failed to generate PDF");
        downloadBtn.textContent = '⚠️ Retry Download';
    } finally {
        downloadBtn.disabled = false;
    }
});

async function startProcessing() {
    try {
        const files = uploadPanel.getFiles();

        if (files.length === 0) {
            alert('Please select an image file first.');
            return;
        }

        const imageFile = files[0];
        if (!imageFile.type.startsWith('image/')) {
            alert('Please upload a valid image file (JPG, PNG).');
            return;
        }

        // Disable process button
        const btn = document.getElementById('processBtn');
        btn.disabled = true;
        btn.textContent = '⏳ Analyzing Scene...';

        updateStatus('Uploading & Analyzing...', 'processing');

        // 1. Display Image Immediately (Client-side preview)
        await scene3D.displayUploadedImages(files);

        // 2. Call VISUAL Analysis API (with green boxes)
        console.log("Calling visual analysis endpoint...");
        const result = await API.analyzeImageVisual(imageFile);

        console.log("Analysis result:", result);

        if (result.success) {
            lastAnalysisResult = result;
            currentCaseId = "IMG_" + Date.now(); // Temp ID for this session

            if (result.session_id) {
                chatHandler.setSessionId(result.session_id);
            }

            // Update Object Count and Confidence
            document.getElementById('objectCount').textContent = result.object_count || 0;
            document.getElementById('avgConfidence').textContent =
                result.avg_confidence ? `${(result.avg_confidence * 100).toFixed(0)}%` : '0%';

            // If we have an annotated image URL, replace the 3D scene image with it
            if (result.annotated_image_url) {
                console.log("Annotated image URL:", result.annotated_image_url);

                // Create a full URL
                const fullUrl = `http://127.0.0.1:5000${result.annotated_image_url}`;

                // Update the scene with annotated image
                const img = new Image();
                img.onload = () => {
                    console.log("Annotated image loaded successfully");
                    // Re-display with the annotated image
                    const annotatedFile = new File([imageFile], imageFile.name, { type: imageFile.type });
                    annotatedFile.annotatedUrl = fullUrl;
                    scene3D.displayAnnotatedImage(fullUrl);
                };
                img.onerror = () => {
                    console.error("Failed to load annotated image");
                };
                img.src = fullUrl;
            }

            // Populate Fact Container (if available from combined endpoint)
            if (result.facts) {
                const facts = result.facts;

                // Show AI Scene Summary
                const summarySection = document.getElementById('summarySection');
                const aiSummaryValue = document.getElementById('aiSummaryValue');
                if (summarySection && facts.scene_summary) {
                    summarySection.style.display = 'block';
                    // Convert newlines to breaks if any
                    aiSummaryValue.innerHTML = facts.scene_summary.replace(/\n/g, '<br>');
                }

                document.getElementById('visualDescription').textContent = facts.one_line_description || "Analysis complete.";

                document.getElementById('objectsValue').textContent = facts.total_object_count || result.object_count || "0";
                document.getElementById('personsValue').textContent = facts.persons?.count || 0;
                document.getElementById('weaponsValue').textContent = facts.weapons?.length || "None";
                document.getElementById('locationValue').textContent = facts.location || "Unknown";

                const actionsDiv = document.getElementById('actionsValue');
                actionsDiv.textContent = facts.actions?.length > 0 ? facts.actions.join(", ") : "No specific actions detected";

                // Populate Evidence Facts List
                const factsList = document.getElementById('evidenceFactsList');
                if (factsList && facts.objects_detected) {
                    factsList.textContent = facts.objects_detected.length > 0 ? facts.objects_detected.join(", ") : "No distinct objects identified";
                }

                // Populate Scenarios
                if (result.scenarios) {
                    const scenariosList = document.getElementById('scenariosList');
                    scenariosList.innerHTML = '';
                    result.scenarios.forEach((scen, index) => {
                        const div = document.createElement('div');
                        div.className = 'scenario-item';
                        div.innerHTML = `<strong>Scenario ${index + 1}:</strong> ${scen}`;
                        scenariosList.appendChild(div);
                    });
                }
            } else {
                // Simple mode - just show detection count
                document.getElementById('visualDescription').textContent = result.message || "Detection complete.";
                document.getElementById('objectsValue').textContent = result.object_count || "0";
            }

            updateStatus('Analysis Complete', 'complete');
            downloadBtn.disabled = false;

        } else {
            throw new Error(result.message || 'Analysis failed');
        }


    } catch (error) {
        console.error('Processing error:', error);
        alert('Error: ' + error.message);
        updateStatus('Processing failed', 'error');
    } finally {
        const btn = document.getElementById('processBtn');
        btn.disabled = false;
        btn.textContent = '🚀 Start Processing';
    }
}

function updateStatus(message, status) {
    console.log(`[${status}] ${message}`);
    // Simple console log or update status panel if we kept it
    // The simplified page might not need a complex status list, but if elements exist:
}
