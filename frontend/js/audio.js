/**
 * Audio Analysis Page Logic
 */

// Initialize components
const uploadPanel = new UploadPanel();
const evidencePanel = new EvidencePanel();
const chatHandler = new ChatHandler('audio');

document.getElementById('processBtn').addEventListener('click', async () => {
    await startProcessing();
});

async function startProcessing() {
    try {
        const files = uploadPanel.getFiles();

        if (files.length === 0) {
            alert('Please select an audio file first.');
            return;
        }

        const audioFile = files[0];
        if (!audioFile.type.startsWith('audio/')) {
            alert('Please upload a valid audio file.');
            return;
        }

        // Disable process button
        const btn = document.getElementById('processBtn');
        btn.disabled = true;
        btn.textContent = '⏳ Processing audio...';

        // Show Blue Box Loader
        const blueBox = document.getElementById('blueBox');
        blueBox.style.display = 'block';
        blueBox.innerHTML = '<strong>Processing audio...</strong> (Reading file & running Whisper-Tiny)';
        blueBox.style.background = '#e3f2fd';
        blueBox.style.color = '#333';

        // Direct Upload using API helper
        const result = await API.analyzeAudio(audioFile);
        console.log("Audio Analysis Result:", result);

        if (result.status === 'success') {
            if (result.session_id) {
                chatHandler.setSessionId(result.session_id);
            }
            // UPDATE BLUE BOX
            blueBox.innerHTML = `<strong>Transcript:</strong><br>${result.transcript}`;
            blueBox.style.background = '#e3f2fd';
            blueBox.style.border = '1px solid #b6d4fe';

            // Update Evidence Panel (Translations & Intelligence)
            // Use 'updateAudioFindings' which we designed to be comprehensive
            if (result.translations) {
                // Construct a result object compatible with EvidencePanel
                const findings = [{
                    transcription: { english: result.transcript },
                    translations: result.translations,
                    summary: result.one_line_summary,
                    crime_analysis: result.crime_analysis,
                    timeline: result.timeline
                }];
                evidencePanel.updateAudioFindings(findings);
            }

            // Render Timeline in the Timeline Panel if it exists
            const timelineBody = document.getElementById('timelineBody');
            const timelineTable = document.getElementById('timelineTable');
            const timelinePlaceholder = document.getElementById('timelinePlaceholder');

            if (timelineBody && result.timeline) {
                timelineBody.innerHTML = '';

                if (result.timeline.length > 0) {
                    result.timeline.forEach(event => {
                        const row = document.createElement('tr');
                        row.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
                        row.innerHTML = `
                            <td style="padding: 8px; font-weight: 600; color: var(--primary); white-space: nowrap;">${event.time || '00:00'}</td>
                            <td style="padding: 8px; font-size: 0.9rem;">${event.event}</td>
                        `;
                        timelineBody.appendChild(row);
                    });

                    timelineTable.style.display = 'table';
                    timelinePlaceholder.style.display = 'none';
                } else {
                    timelineTable.style.display = 'none';
                    timelinePlaceholder.innerHTML = '<p>No major crime events detected in audio.</p>';
                    timelinePlaceholder.style.display = 'block';
                }
            }

        } else {
            throw new Error(result.message || 'Unknown error');
        }

    } catch (error) {
        console.error('Processing error:', error);
        const blueBox = document.getElementById('blueBox');
        blueBox.innerHTML = `<strong>Error:</strong> ${error.message}`;
        blueBox.style.background = '#f8d7da';
        blueBox.style.color = '#721c24';
    } finally {
        const btn = document.getElementById('processBtn');
        btn.disabled = false;
        btn.textContent = '🚀 Start Processing';
    }
}
