/**
 * API Client for Crime Scene Reconstruction System
 */

const API_BASE_URL = 'http://localhost:5000/api';

class API {
    /**
     * Upload a single file
     */
    static async uploadFile(file, caseId = null) {
        const formData = new FormData();
        formData.append('file', file);
        if (caseId) {
            formData.append('case_id', caseId);
        }

        const response = await fetch(`${API_BASE_URL}/upload/file`, {
            method: 'POST',
            body: formData
        });

        return await response.json();
    }

    /**
     * Upload multiple files
     */
    static async uploadBatch(files, caseId = null) {
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });
        if (caseId) {
            formData.append('case_id', caseId);
        }

        const response = await fetch(`${API_BASE_URL}/upload/batch`, {
            method: 'POST',
            body: formData
        });

        return await response.json();
    }

    /**
     * Process vision data
     */
    static async processVision(caseId) {
        const response = await fetch(`${API_BASE_URL}/process/vision/${caseId}`, {
            method: 'POST'
        });

        return await response.json();
    }

    /**
     * Process audio data
     */
    static async processAudio(caseId) {
        const response = await fetch(`${API_BASE_URL}/process/audio/${caseId}`, {
            method: 'POST'
        });

        return await response.json();
    }

    /**
     * Process text data
     */
    static async processText(caseId) {
        const response = await fetch(`${API_BASE_URL}/process/text/${caseId}`, {
            method: 'POST'
        });

        return await response.json();
    }

    /**
     * Process fusion
     */
    static async processFusion(caseId, visionResults, audioResults, textResults) {
        const response = await fetch(`${API_BASE_URL}/process/fusion/${caseId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                vision_results: visionResults,
                audio_results: audioResults,
                text_results: textResults
            })
        });

        return await response.json();
    }

    /**
     * Generate timeline
     */
    static async generateTimeline(caseId, visionResults, audioResults, textResults, fusionResults) {
        const response = await fetch(`${API_BASE_URL}/process/timeline/${caseId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                vision_results: visionResults,
                audio_results: audioResults,
                text_results: textResults,
                fusion_results: fusionResults
            })
        });

        return await response.json();
    }

    /**
     * Reconstruct 3D scene
     */
    static async reconstructScene(caseId, visionResults, fusionResults) {
        const response = await fetch(`${API_BASE_URL}/process/reconstruct/${caseId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                vision_results: visionResults,
                fusion_results: fusionResults
            })
        });

        return await response.json();
    }

    /**
     * Generate report
     */
    static async generateReport(caseId, allResults) {
        const response = await fetch(`${API_BASE_URL}/process/report/${caseId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(allResults)
        });

        return await response.json();
    }

    /**
     * Run complete pipeline
     */
    static async processCompletePipeline(caseId) {
        const response = await fetch(`${API_BASE_URL}/process/complete/${caseId}`, {
            method: 'POST'
        });

        return await response.json();
    }

    /**
     * Get 3D scene data
     */
    static async getScene(caseId) {
        const response = await fetch(`${API_BASE_URL}/results/scene/${caseId}`);
        return await response.json();
    }

    /**
     * Get case summary
     */
    static async getCaseSummary(caseId) {
        const response = await fetch(`${API_BASE_URL}/results/summary/${caseId}`);
        return await response.json();
    }

    /**
     * Download JSON report
     */
    static getJsonReportUrl(caseId) {
        return `${API_BASE_URL}/results/report/json/${caseId}`;
    }

    /**
     * Download PDF report
     */
    static getPdfReportUrl(caseId) {
        return `${API_BASE_URL}/results/report/pdf/${caseId}`;
    }

    /**
     * Direct Audio Analysis (Fast Path)
     */
    static async analyzeAudio(file) {
        const formData = new FormData();
        formData.append('audio', file);

        const response = await fetch(`${API_BASE_URL}/analyze-audio`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    }

    /**
     * Video Analysis (New)
     */
    static async analyzeVideo(file) {
        const formData = new FormData();
        formData.append('video', file);
        const response = await fetch(`${API_BASE_URL}/analyze-video`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        return await response.json();
    }

    /**
     * AI Chat System (Unified)
     */
    static async chat(mode, session_id, question) {
        const response = await fetch(`${API_BASE_URL}/chat/${mode}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id, question })
        });
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        return await response.json();
    }

    /**
     * Direct Image Analysis (Detailed)
     */
    static async analyzeImage(file) {
        const formData = new FormData();
        formData.append('image', file);

        const response = await fetch(`${API_BASE_URL}/process/analyze-image`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    }

    /**
     * Visual Image Analysis (Returns annotated image with green boxes)
     */
    static async analyzeImageVisual(file) {
        const formData = new FormData();
        formData.append('image', file);

        const response = await fetch(`${API_BASE_URL}/process/analyze-image-visual`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    }

    /**
     * Generate Image Report PDF
     */
    static async generateImageReport(caseId, payload) {
        const response = await fetch(`${API_BASE_URL}/process/report/image/${caseId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        return await response.json();
    }
}
