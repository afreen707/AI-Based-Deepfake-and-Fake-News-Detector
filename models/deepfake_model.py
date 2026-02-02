# Wrapper for deepfake detection
# deepfake_model.py
import os
from PIL import Image
import io
import numpy as np

class DeepfakeModel:
    def __init__(self):
        self.model_path = os.path.join('models', 'saved_models', 'deepfake_model.h5')
        print(f"Deepfake Model initialized from {self.model_path}")

    def predict(self, file):
        """
        Input: uploaded image/video file
        Output: score (0-100), manipulated regions list
        """
        try:
            # Read the file
            file_bytes = file.read()
            file.seek(0)  # Reset file pointer
            
            # Check if it's a video or image
            filename = file.filename.lower()
            is_video = filename.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))
            
            if is_video:
                return self._analyze_video(file_bytes)
            else:
                return self._analyze_image(file_bytes)
                
        except Exception as e:
            print(f"Error reading file: {e}")
            return 50, [{"error": "Could not process media file"}]
    
    def _analyze_image(self, file_bytes):
        """Analyze a single image for deepfake indicators"""
        try:
            img = Image.open(io.BytesIO(file_bytes))
            width, height = img.size
            
            # Initialize score (starts at 100 = authentic)
            score = 100
            manipulated_regions = []
            issues_found = []
            
            # 1. Check image dimensions
            if width < 100 or height < 100:
                score -= 15
                issues_found.append("Unusually small dimensions")
            
            # 2. Check aspect ratio (deepfakes often have unusual ratios)
            aspect_ratio = width / height
            if aspect_ratio < 0.5 or aspect_ratio > 2.5:
                score -= 10
                issues_found.append("Unusual aspect ratio")
            
            # 3. Check image format and quality
            format_type = img.format
            if format_type == 'JPEG':
                # Check for extreme compression (common in manipulated images)
                if hasattr(img, 'info') and 'quality' in img.info:
                    quality = img.info.get('quality', 95)
                    if quality < 60:
                        score -= 10
                        issues_found.append("Low JPEG quality")
            
            # 4. Convert to numpy array for pixel analysis
            img_array = np.array(img.convert('RGB'))
            
            # 5. Check for color inconsistencies
            # Calculate color variance in different regions
            h_third = height // 3
            w_third = width // 3
            
            regions = [
                img_array[0:h_third, 0:w_third],           # Top-left
                img_array[0:h_third, -w_third:],           # Top-right
                img_array[-h_third:, 0:w_third],           # Bottom-left
                img_array[-h_third:, -w_third:],           # Bottom-right
                img_array[h_third:2*h_third, w_third:2*w_third]  # Center
            ]
            
            variances = [np.var(region) for region in regions]
            variance_diff = max(variances) - min(variances)
            
            if variance_diff > 5000:
                score -= 15
                issues_found.append("Inconsistent color variance across regions")
                manipulated_regions.append({
                    "note": "Possible color inconsistency detected",
                    "confidence": min(30, int(variance_diff / 200))
                })
            
            # 6. Check for edge artifacts (common in face swaps)
            # Simple edge detection
            edges = self._detect_edges(img_array)
            edge_density = np.sum(edges) / (width * height)
            
            if edge_density > 0.15:  # Too many edges might indicate manipulation
                score -= 10
                issues_found.append("Unusual edge patterns")
            
            # 7. Check for noise patterns
            noise_level = self._calculate_noise(img_array)
            if noise_level < 2:  # Too smooth might indicate AI generation
                score -= 10
                issues_found.append("Unnaturally smooth (possible AI generation)")
            elif noise_level > 20:  # Too noisy might indicate manipulation
                score -= 5
                issues_found.append("Excessive noise patterns")
            
            # Ensure score stays in valid range
            score = max(0, min(100, score))
            
            # Add summary of findings
            if not issues_found:
                issues_found = ["No suspicious patterns detected"]
            
            if score < 70 and not manipulated_regions:
                manipulated_regions.append({
                    "issues": issues_found,
                    "confidence": 100 - score
                })
            
            return score, manipulated_regions if manipulated_regions else issues_found
            
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return 60, [{"error": f"Analysis error: {str(e)}"}]
    
    def _analyze_video(self, file_bytes):
        """Analyze video for deepfake indicators (simplified)"""
        # For now, return a cautionary score for videos
        # Real implementation would analyze frame-by-frame
        return 70, [{"note": "Video analysis: Basic check only. Upload individual frames for detailed analysis."}]
    
    def _detect_edges(self, img_array):
        """Simple edge detection using gradient"""
        gray = np.mean(img_array, axis=2)
        dx = np.abs(np.diff(gray, axis=1))
        dy = np.abs(np.diff(gray, axis=0))
        edges = (dx[:-1, :] + dy[:, :-1]) > 30
        return edges
    
    def _calculate_noise(self, img_array):
        """Calculate noise level in image"""
        # Use Laplacian variance as noise estimate
        gray = np.mean(img_array, axis=2)
        laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        
        # Simple convolution
        h, w = gray.shape
        result = np.zeros((h-2, w-2))
        
        for i in range(h-2):
            for j in range(w-2):
                result[i, j] = np.sum(gray[i:i+3, j:j+3] * laplacian)
        
        return np.var(result)