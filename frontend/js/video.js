document.addEventListener('DOMContentLoaded', () => {
    const videoInput = document.getElementById('videoInput');
    const videoUploadZone = document.getElementById('videoUploadZone');
    const processBtn = document.getElementById('processBtn');
    const fileInfo = document.getElementById('fileInfo');
    const videoPreviewContainer = document.getElementById('videoPreviewContainer');
    const chatHandler = new ChatHandler('video');

    videoUploadZone.addEventListener('click', () => videoInput.click());

    videoInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            fileInfo.innerHTML = `
                <div class="uploaded-file">
                    <span>🎥 ${file.name}</span>
                    <span>${(file.size / (1024 * 1024)).toFixed(1)} MB</span>
                </div>
            `;
            processBtn.disabled = false;

            // Show preview
            const url = URL.createObjectURL(file);
            videoPreviewContainer.innerHTML = `<video controls src="${url}"></video>`;
        }
    });

    processBtn.addEventListener('click', async () => {
        const file = videoInput.files[0];
        if (!file) return;

        try {
            processBtn.disabled = true;
            processBtn.innerHTML = '⏳ Analyzing Video...';

            // Reset UI
            document.getElementById('summaryPanel').style.display = 'none';
            document.getElementById('objectsPanel').style.display = 'none';
            document.getElementById('timelinePanel').style.display = 'none';

            const result = await API.analyzeVideo(file);
            console.log("Video Analysis Result:", result);

            if (result.status === 'success') {
                if (result.session_id) {
                    chatHandler.setSessionId(result.session_id);
                }
                renderResults(result);
            } else {
                alert("Error: " + result.message);
            }
        } catch (error) {
            console.error("Video processing error:", error);
            alert("Unexpected error during video analysis.");
        } finally {
            processBtn.disabled = false;
            processBtn.innerHTML = '🚀 Start Analysis';
        }
    });

    function renderResults(data) {
        // 1. Description
        document.getElementById('summaryPanel').style.display = 'block';
        document.getElementById('videoDescription').textContent = data.video_description;

        // 2. Crime Badge
        const badgeContainer = document.getElementById('crimeBadgeContainer');
        const crime = data.crime_type;
        badgeContainer.innerHTML = `
            <div class="crime-badge badge-${crime.label.toLowerCase()}">
                ${crime.label} (${(crime.confidence * 100).toFixed(0)}%)
            </div>
            <p style="font-size: 11px; color: #888; margin-top: -5px; margin-bottom: 15px;">Reason: ${crime.reason}</p>
        `;

        // 3. Structured Metrics (Objects, People, Location, Action)
        document.getElementById('objectsPanel').style.display = 'block';
        const objectPanel = document.getElementById('objectsPanel');
        objectPanel.querySelector('.panel-title').textContent = '📊 Scene Intelligence';

        const metrics = data.crime_type.extracted_metrics;
        const objectList = document.getElementById('objectList');
        objectList.innerHTML = `
            <div class="evidence-item">
                <div class="evidence-label">Objects Detect</div>
                <div class="evidence-value" style="color: #fff;">${metrics.objects.join(', ')}</div>
            </div>
            <div class="evidence-item">
                <div class="evidence-label">People Count</div>
                <div class="evidence-value" style="color: #fff;">${metrics.people_count}</div>
            </div>
            <div class="evidence-item">
                <div class="evidence-label">Location</div>
                <div class="evidence-value" style="color: #2ecc71;">${metrics.location}</div>
            </div>
            <div class="evidence-item">
                <div class="evidence-label">Action</div>
                <div class="evidence-value" style="color: #3498db;">${metrics.action}</div>
            </div>
        `;

        // 4. Timeline
        document.getElementById('timelinePanel').style.display = 'block';
        const timelineBody = document.getElementById('timelineBody');
        timelineBody.innerHTML = data.timeline.map(event => `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="font-family: 'Courier New', monospace; color: var(--primary); font-weight: 600; padding: 10px; white-space: nowrap;">${event.time}</td>
                <td style="padding: 10px; font-size: 13px; color: #eee;">${event.event}</td>
            </tr>
        `).join('');
    }
});
