/* ═══════════════════════════════════════════════════
   Camera & Photo handling
   - File input trigger
   - Client-side preview
   - Image compression via Canvas
   ═══════════════════════════════════════════════════ */

(function () {
    'use strict';

    const MAX_WIDTH = 1200;
    const MAX_HEIGHT = 1200;
    const QUALITY = 0.8;

    const uploadArea = document.getElementById('photoUploadArea');
    const photoInput = document.getElementById('photoInput');
    const previewEl = document.getElementById('photoPreview');
    const previewImg = document.getElementById('previewImg');
    const placeholder = document.getElementById('photoPlaceholder');
    const removeBtn = document.getElementById('removePhoto');

    if (!uploadArea || !photoInput) return;

    // Click area → open file picker
    uploadArea.addEventListener('click', function (e) {
        if (e.target.closest('#removePhoto')) return;
        photoInput.click();
    });

    // File selected
    photoInput.addEventListener('change', function () {
        const file = this.files[0];
        if (!file) return;

        compressImage(file, function (compressedBlob) {
            // Replace file input with compressed version
            const dataTransfer = new DataTransfer();
            const compressedFile = new File([compressedBlob], file.name, {
                type: compressedBlob.type,
                lastModified: Date.now(),
            });
            dataTransfer.items.add(compressedFile);
            photoInput.files = dataTransfer.files;

            // Show preview
            const url = URL.createObjectURL(compressedBlob);
            previewImg.src = url;
            previewEl.style.display = 'block';
            placeholder.style.display = 'none';
        });
    });

    // Remove photo
    if (removeBtn) {
        removeBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            photoInput.value = '';
            previewEl.style.display = 'none';
            placeholder.style.display = 'flex';
            previewImg.src = '';
        });
    }

    /**
     * Compress an image file using Canvas.
     * Resizes to MAX_WIDTH x MAX_HEIGHT and compresses to JPEG.
     */
    function compressImage(file, callback) {
        // Skip non-image files
        if (!file.type.startsWith('image/')) {
            callback(file);
            return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            const img = new Image();
            img.onload = function () {
                let width = img.width;
                let height = img.height;

                // Calculate new dimensions
                if (width > MAX_WIDTH || height > MAX_HEIGHT) {
                    const ratio = Math.min(MAX_WIDTH / width, MAX_HEIGHT / height);
                    width = Math.round(width * ratio);
                    height = Math.round(height * ratio);
                }

                // Draw to canvas
                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);

                // Export as blob
                canvas.toBlob(
                    function (blob) {
                        callback(blob || file);
                    },
                    'image/jpeg',
                    QUALITY
                );
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
})();
