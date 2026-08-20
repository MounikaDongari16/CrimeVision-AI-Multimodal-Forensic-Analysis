/**
 * Evidence Panel Component
 */

class EvidencePanel {
    constructor() {
        this.tabs = document.querySelectorAll('.tab-btn');
        this.tabContents = document.querySelectorAll('.tab-content');

        this.init();
    }

    init() {
        // Tab switching
        this.tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        this.tabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });

        // Update tab contents
        this.tabContents.forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });

        // Initialize metrics container if it doesn't exist
        if (!document.getElementById('metrics-container')) {
            const factsTab = document.getElementById('facts-tab');
            const metricsDiv = document.createElement('div');
            metricsDiv.id = 'metrics-container';
            factsTab.prepend(metricsDiv);
        }
    }

    updateMetrics(summary) {
        const container = document.getElementById('metrics-container');
        if (!container || !summary) return;

        container.innerHTML = `
            <div class="evidence-metrics" style="background: rgba(46, 204, 113, 0.1); border-radius: 8px; padding: 15px; margin-bottom: 20px; border-left: 4px solid #2ecc71;">
                <h4 style="margin: 0 0 10px 0; color: #2ecc71; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;">AI Scene Analysis</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div>
                        <div style="font-size: 10px; color: #888;">Detected Location</div>
                        <div style="font-weight: bold; color: #fff;">${summary.location?.toUpperCase() || 'UNKNOWN'}</div>
                    </div>
                    <div>
                        <div style="font-size: 10px; color: #888;">People Count</div>
                        <div style="font-weight: bold; color: #fff;">${summary.people_count || 0}</div>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <div style="font-size: 10px; color: #888;">Weaponry</div>
                    <div style="font-weight: bold; color: #e74c3c;">${summary.weapon_types?.length > 0 ? summary.weapon_types.join(', ').toUpperCase() : 'NONE DETECTED'}</div>
                </div>
            </div>
        `;
    }

    updateAudioFindings(audioResults) {
        // Find or fallback container
        const factsTab = document.getElementById('facts-tab');
        let enrichedContainer = document.getElementById('enriched-findings');

        if (!enrichedContainer && factsTab) {
            factsTab.insertAdjacentHTML('afterbegin', '<div id="enriched-findings"></div>');
            enrichedContainer = document.getElementById('enriched-findings');
        }

        if (!enrichedContainer || !audioResults || audioResults.length === 0) return;

        // Clear old audio box
        const oldAudio = document.getElementById('audio-box');
        if (oldAudio) oldAudio.remove();

        // Helper to get safe text
        const safe = (txt) => txt || 'Unavailable';

        let audioHtml = `
            <div id="audio-box" class="audio-findings" style="margin-bottom: 25px; font-family: 'Inter', sans-serif;">
                
                <!-- 1. One-Line Summary Card -->
                <div style="background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); padding: 15px; border-radius: 8px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; margin-bottom: 5px;">AI Summary</div>
                    <div style="font-size: 14px; font-weight: 500; line-height: 1.4;">"${safe(audioResults[0].summary)}"</div>
                </div>

                <!-- 2. Crime Analysis Panel (Metrics) -->
                ${audioResults[0].crime_analysis ? `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px;">
                    <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px;">
                        <div style="font-size: 10px; color: #aaa;">Event Type</div>
                        <div style="font-weight: bold; color: #e74c3c;">${safe(audioResults[0].crime_analysis.event).toUpperCase()}</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px;">
                        <div style="font-size: 10px; color: #aaa;">Location</div>
                        <div style="font-weight: bold; color: #2ecc71;">${safe(audioResults[0].crime_analysis.location).toUpperCase()}</div>
                    </div>
                </div>
                ` : ''}

                <!-- 3. Tabbed Translations & Transcript Box -->
                <div class="evidence-category" style="margin-bottom: 10px;"><strong>📜 Transcripts & Translations:</strong></div>
                <div style="background: #1a1a1a; border-radius: 8px; border: 1px solid #333; overflow: hidden; margin-bottom: 20px;">
                    <div style="display: flex; border-bottom: 1px solid #333; background: #252525;">
                        <button onclick="document.querySelectorAll('.trans-tab').forEach(e=>e.style.display='none');document.getElementById('tab-en').style.display='block';" style="flex:1; padding: 10px; border:none; background:transparent; color:#ccc; cursor:pointer; font-size:11px;">English</button>
                        <button onclick="document.querySelectorAll('.trans-tab').forEach(e=>e.style.display='none');document.getElementById('tab-hi').style.display='block';" style="flex:1; padding: 10px; border:none; background:transparent; color:#ccc; cursor:pointer; font-size:11px;">Hindi</button>
                        <button onclick="document.querySelectorAll('.trans-tab').forEach(e=>e.style.display='none');document.getElementById('tab-te').style.display='block';" style="flex:1; padding: 10px; border:none; background:transparent; color:#ccc; cursor:pointer; font-size:11px;">Telugu</button>
                        <button onclick="document.querySelectorAll('.trans-tab').forEach(e=>e.style.display='none');document.getElementById('tab-fr').style.display='block';" style="flex:1; padding: 10px; border:none; background:transparent; color:#ccc; cursor:pointer; font-size:11px;">French</button>
                    </div>
                    
                    <!-- Content Areas -->
                    <div id="tab-en" class="trans-tab" style="padding: 15px; max-height: 150px; overflow-y: auto; font-size: 12px; line-height: 1.5; color: #ddd;">
                        ${safe(audioResults[0].transcription?.english)}
                    </div>
                    <div id="tab-hi" class="trans-tab" style="display:none; padding: 15px; max-height: 150px; overflow-y: auto; font-size: 12px; line-height: 1.5; color: #ddd;">
                        ${safe(audioResults[0].translations?.hindi)}
                    </div>
                    <div id="tab-te" class="trans-tab" style="display:none; padding: 15px; max-height: 150px; overflow-y: auto; font-size: 12px; line-height: 1.5; color: #ddd;">
                        ${safe(audioResults[0].translations?.telugu)}
                    </div>
                    <div id="tab-fr" class="trans-tab" style="display:none; padding: 15px; max-height: 150px; overflow-y: auto; font-size: 12px; line-height: 1.5; color: #ddd;">
                        ${safe(audioResults[0].translations?.french)}
                    </div>
                </div>
                </div>

            </div>
        `;

        enrichedContainer.insertAdjacentHTML('beforeend', audioHtml);
    }

    updateDetections(detections) {
        const container = document.getElementById('detections-tab');

        if (!detections || detections.length === 0) {
            container.innerHTML = '<div class="evidence-placeholder"><p>No detections yet</p></div>';
            return;
        }

        let html = '';
        detections.forEach(det => {
            html += `
                <div class="evidence-item">
                    <div class="evidence-label">${det.label}</div>
                    <div class="evidence-value">Confidence: ${(det.confidence * 100).toFixed(1)}%</div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    updateFacts(facts) {
        const container = document.getElementById('general-facts');

        if (!facts || !container) {
            return;
        }

        let html = '';

        Object.entries(facts).forEach(([category, items]) => {
            if (items && items.length > 0) {
                html += `<div class="evidence-category"><strong>${category}:</strong></div>`;
                items.forEach(item => {
                    html += `<div class="evidence-item"><div class="evidence-value">${item}</div></div>`;
                });
            }
        });

        container.innerHTML = html;
    }

    updateEntities(entities) {
        const container = document.getElementById('entities-tab');

        if (!entities) {
            container.innerHTML = '<div class="evidence-placeholder"><p>No entities extracted yet</p></div>';
            return;
        }

        let html = '';

        Object.entries(entities).forEach(([category, items]) => {
            if (items && items.length > 0) {
                html += `<div class="evidence-category"><strong>${category}:</strong></div>`;
                items.forEach(item => {
                    const value = typeof item === 'object' ? item.value : item;
                    html += `<div class="evidence-item"><div class="evidence-value">${value}</div></div>`;
                });
            }
        });

        container.innerHTML = html || '<div class="evidence-placeholder"><p>No entities extracted yet</p></div>';
    }
}
