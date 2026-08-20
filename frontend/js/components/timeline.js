/**
 * Timeline Component
 */

class Timeline {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(timelineData) {
        if (!timelineData || !timelineData.events || timelineData.events.length === 0) {
            this.container.innerHTML = '<div class="timeline-placeholder"><p>No timeline events available</p></div>';
            return;
        }

        const events = timelineData.events;

        let html = '<div class="timeline-events">';

        events.forEach((event, index) => {
            const time = event.timestamp !== null
                ? this.formatTimestamp(event.timestamp)
                : 'Unknown time';

            const certaintyClass = event.certainty || 'medium';

            html += `
                <div class="timeline-event" data-certainty="${certaintyClass}">
                    <div class="timeline-time">${time}</div>
                    <div class="timeline-description">${event.description}</div>
                    <div class="timeline-meta">
                        <span class="timeline-source">${event.source}</span>
                        <span class="timeline-confidence">Confidence: ${(event.confidence * 100).toFixed(0)}%</span>
                    </div>
                </div>
            `;
        });

        html += '</div>';

        this.container.innerHTML = html;
    }

    formatTimestamp(timestamp) {
        if (typeof timestamp === 'number') {
            const minutes = Math.floor(timestamp / 60);
            const seconds = Math.floor(timestamp % 60);
            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        return timestamp;
    }

    clear() {
        this.container.innerHTML = '<div class="timeline-placeholder"><p>Timeline will be generated after processing</p></div>';
    }
}
