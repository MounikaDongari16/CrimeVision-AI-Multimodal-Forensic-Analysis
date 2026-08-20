/**
 * 3D Scene Viewer using Three.js
 */

class Scene3D {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.objects = [];
        this.uploadedImages = [];  // Store uploaded image planes
        this.detectionBoxes = [];  // Store bounding box meshes
        this.detectionBoxes = [];  // Store bounding box meshes

        this.init();
    }

    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0f1e);

        // Create camera
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        this.camera.position.set(0, 15, 12); // Centered vertically at room height 15
        this.camera.lookAt(0, 15, 0);        // Looking at the center of the image

        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(window.devicePixelRatio);

        // Clear placeholder and add renderer
        this.container.innerHTML = '';
        this.container.appendChild(this.renderer.domElement);

        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 10);
        this.scene.add(directionalLight);

        // Grid removed for plain background as requested

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());

        // Start animation loop
        this.animate();
    }

    loadSceneData(sceneData) {
        // Clear existing objects
        this.clearScene();

        // Add room
        if (sceneData.room) {
            this.addRoom(sceneData.room);
        }

        // Add objects
        if (sceneData.objects) {
            sceneData.objects.forEach(obj => this.addObject(obj));
        }

        // Update info
        this.updateSceneInfo(sceneData);
    }

    addRoom(roomData) {
        const { dimensions } = roomData;

        // Create floor (plain dark floor without lines)
        const floorGeometry = new THREE.PlaneGeometry(dimensions.width, dimensions.depth);
        const floorMaterial = new THREE.MeshStandardMaterial({
            color: 0x0a0f1e, // Match background for a seamless plain look
            side: THREE.DoubleSide
        });
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        this.scene.add(floor);

        // Room wireframe removed for plain view as requested
    }

    addObject(objectData) {
        const { position, size, color, label } = objectData;

        // Create box geometry
        const geometry = new THREE.BoxGeometry(size[0], size[2], size[1]);
        const material = new THREE.MeshStandardMaterial({
            color: new THREE.Color(color[0], color[1], color[2]),
            transparent: true,
            opacity: 0.8
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(position[0], position[2] + size[2] / 2, position[1]);

        // Add outline
        const edges = new THREE.EdgesGeometry(geometry);
        const lineMaterial = new THREE.LineBasicMaterial({ color: 0xffffff });
        const wireframe = new THREE.LineSegments(edges, lineMaterial);
        mesh.add(wireframe);

        // Store metadata
        mesh.userData = objectData;

        this.scene.add(mesh);
        this.objects.push(mesh);
    }

    clearScene() {
        // Remove all objects
        this.objects.forEach(obj => {
            this.scene.remove(obj);
            obj.geometry.dispose();
            obj.material.dispose();
        });
        this.objects = [];

        // Clear detections too
        this.detectionBoxes.forEach(box => {
            this.scene.remove(box);
            if (box.geometry) box.geometry.dispose();
            if (box.material) box.material.dispose();
        });
        this.detectionBoxes = [];
    }

    resetView() {
        this.camera.position.set(0, 15, 12);
        this.camera.lookAt(0, 15, 0);
    }

    updateSceneInfo(sceneData) {
        const objectCount = sceneData.objects ? sceneData.objects.length : 0;
        const avgConfidence = sceneData.objects
            ? (sceneData.objects.reduce((sum, obj) => sum + obj.confidence, 0) / objectCount * 100).toFixed(0)
            : 0;

        document.getElementById('objectCount').textContent = objectCount;
        document.getElementById('avgConfidence').textContent = avgConfidence + '%';
    }

    onWindowResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize(width, height);
    }

    displayUploadedImages(imageFiles) {
        return new Promise((resolve, reject) => {
            // Clear previous images
            this.uploadedImages.forEach(img => {
                this.scene.remove(img);
                if (img.material.map) img.material.map.dispose();
                img.material.dispose();
                img.geometry.dispose();
            });
            this.uploadedImages = [];

            const loadPromises = [];

            // Display each image as a plane in the scene
            imageFiles.forEach((file, index) => {
                if (file.type && file.type.startsWith('image/')) {
                    const p = new Promise((resolveLoad) => {
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            const textureLoader = new THREE.TextureLoader();
                            textureLoader.load(e.target.result, (texture) => {
                                // Calculate aspect ratio
                                const aspectRatio = texture.image.width / texture.image.height;

                                // Room dimensions (even larger to support bigger planes)
                                const roomWidth = 60;
                                const roomHeight = 30;
                                const roomDepth = 30;

                                // Scale image to be truly massive
                                let planeWidth = roomWidth - 2;
                                let planeHeight = planeWidth / aspectRatio;

                                if (planeHeight > roomHeight - 2) {
                                    planeHeight = roomHeight - 2;
                                    planeWidth = planeHeight * aspectRatio;
                                }

                                // Create plane geometry
                                const geometry = new THREE.PlaneGeometry(planeWidth, planeHeight);
                                const material = new THREE.MeshBasicMaterial({
                                    map: texture,
                                    side: THREE.DoubleSide,
                                    transparent: false  // Solid for better visibility
                                });

                                const plane = new THREE.Mesh(geometry, material);

                                // Position images perfectly centered in the 30-unit high room
                                plane.position.set(0, 15, -14.5);

                                this.scene.add(plane);
                                this.uploadedImages.push(plane);

                                // Store dimensions for detection mapping
                                plane.userData = {
                                    width: planeWidth,
                                    height: planeHeight,
                                    originalWidth: texture.image.width,
                                    originalHeight: texture.image.height
                                };
                                resolveLoad(plane);
                            });
                        };
                        reader.readAsDataURL(file);
                    });
                    loadPromises.push(p);
                }
            });

            Promise.all(loadPromises).then(() => {
                resolve();
            });
        });
    }

    displayAnnotatedImage(imageUrl) {
        /**
         * Display an annotated image (with green boxes already drawn)
         */
        // Clear previous images
        this.uploadedImages.forEach(img => {
            this.scene.remove(img);
            if (img.material.map) img.material.map.dispose();
            img.material.dispose();
            img.geometry.dispose();
        });
        this.uploadedImages = [];

        const textureLoader = new THREE.TextureLoader();
        textureLoader.load(imageUrl, (texture) => {
            const aspectRatio = texture.image.width / texture.image.height;

            const roomWidth = 60;
            const roomHeight = 30;

            let planeWidth = roomWidth - 2;
            let planeHeight = planeWidth / aspectRatio;

            if (planeHeight > roomHeight - 2) {
                planeHeight = roomHeight - 2;
                planeWidth = planeHeight * aspectRatio;
            }

            const geometry = new THREE.PlaneGeometry(planeWidth, planeHeight);
            const material = new THREE.MeshBasicMaterial({
                map: texture,
                side: THREE.DoubleSide,
                transparent: false
            });

            const plane = new THREE.Mesh(geometry, material);
            plane.position.set(0, 15, -14.5);

            this.scene.add(plane);
            this.uploadedImages.push(plane);

            plane.userData = {
                width: planeWidth,
                height: planeHeight,
                originalWidth: texture.image.width,
                originalHeight: texture.image.height
            };
        });
    }

    drawDetections(detections) {
        // Clear previous boxes
        this.detectionBoxes.forEach(box => {
            this.scene.remove(box);
            if (box.geometry) box.geometry.dispose();
            if (box.material) box.material.dispose();
        });
        this.detectionBoxes = [];

        if (!detections || detections.length === 0 || this.uploadedImages.length === 0) return;

        // Use the last uploaded image as the reference for now
        const imagePlane = this.uploadedImages[this.uploadedImages.length - 1];
        const { width, height, originalWidth, originalHeight } = imagePlane.userData;

        detections.forEach((det, index) => {
            const { bbox, label } = det;

            // Map pixel coordinates to world coordinates
            const x1 = (bbox.x1 / originalWidth - 0.5) * width;
            const y1 = (0.5 - bbox.y1 / originalHeight) * height + 15;
            const x2 = (bbox.x2 / originalWidth - 0.5) * width;
            const y2 = (0.5 - bbox.y2 / originalHeight) * height + 15;

            const boxWidth = Math.abs(x2 - x1);
            const boxHeight = Math.abs(y2 - y1);
            const centerX = (x1 + x2) / 2;
            const centerY = (y1 + y2) / 2;

            // Create a dedicated line object for better visibility
            // Ensure Z-offset is sufficient to prevent Z-fighting (Image at -14.5)
            const zOffset = -14.0;

            // Define vertices for the box outline
            const vertices = new Float32Array([
                x1, y1, zOffset, x2, y1, zOffset, // Top edge
                x2, y1, zOffset, x2, y2, zOffset, // Right edge
                x2, y2, zOffset, x1, y2, zOffset, // Bottom edge
                x1, y2, zOffset, x1, y1, zOffset  // Left edge
            ]);

            const geometry = new THREE.BufferGeometry();
            geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

            const material = new THREE.LineBasicMaterial({
                color: 0x00ff00,
                linewidth: 3, // Note: WebGL often ignores linewidth > 1, but harmless
                depthTest: false, // Force it to always draw on top
                transparent: true,
                opacity: 1.0
            });

            const boxLine = new THREE.LineSegments(geometry, material);
            // Render order ensures it draws after the image plane
            boxLine.renderOrder = 999;

            this.scene.add(boxLine);
            this.detectionBoxes.push(boxLine);
        });
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        // Simple render loop without auto-rotation
        this.renderer.render(this.scene, this.camera);
    }
}
