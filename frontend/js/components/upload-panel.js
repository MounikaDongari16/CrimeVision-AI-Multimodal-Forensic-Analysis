/**
 * Upload Panel Component
 */

class UploadPanel {
    constructor() {
        this.zones = {
            image: {
                el: document.getElementById('imageUploadZone'),
                input: document.getElementById('imageInput')
            },
            audio: {
                el: document.getElementById('audioUploadZone'),
                input: document.getElementById('audioInput')
            },
            video: {
                el: document.getElementById('videoUploadZone'),
                input: document.getElementById('videoInput')
            }
        };
        this.uploadedFilesContainer = document.getElementById('uploadedFiles');
        this.files = [];

        this.init();
    }

    init() {
        Object.entries(this.zones).forEach(([type, zone]) => {
            if (!zone.el || !zone.input) return;

            // Click to upload
            zone.el.addEventListener('click', () => {
                zone.input.click();
            });

            // File input change
            zone.input.addEventListener('change', (e) => {
                this.handleFiles(Array.from(e.target.files), type);
            });

            // Drag and drop
            zone.el.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.el.classList.add('dragover');
            });

            zone.el.addEventListener('dragleave', () => {
                zone.el.classList.remove('dragover');
            });

            zone.el.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.el.classList.remove('dragover');
                this.handleFiles(Array.from(e.dataTransfer.files), type);
            });
        });
    }

    handleFiles(newFiles, category) {
        // Tag files with category if needed, but for now just add to list
        const taggedFiles = newFiles.map(file => {
            file.category = category;
            return file;
        });

        this.files = [...this.files, ...taggedFiles];
        this.renderFiles();

        // Enable process button if files exist
        document.getElementById('processBtn').disabled = this.files.length === 0;
    }

    renderFiles() {
        if (this.files.length === 0) {
            this.uploadedFilesContainer.innerHTML = '';
            return;
        }

        let html = '';
        this.files.forEach((file, index) => {
            const sizeKB = (file.size / 1024).toFixed(1);
            html += `
                <div class="file-item">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${sizeKB} KB</span>
                </div>
            `;
        });

        this.uploadedFilesContainer.innerHTML = html;
    }

    getFiles() {
        return this.files;
    }

    clear() {
        this.files = [];
        this.renderFiles();

        // Clear all inputs
        Object.values(this.zones).forEach(zone => {
            if (zone.input) zone.input.value = '';
        });

        document.getElementById('processBtn').disabled = true;
    }
}
