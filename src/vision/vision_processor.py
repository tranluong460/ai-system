"""
Computer Vision, OCR và Visual Question Answering
"""
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance
import os
import base64
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class VisionProcessor:
    """Computer Vision processor"""
    
    def __init__(self):
        self.temp_dir = "data/temp/vision"
        os.makedirs(self.temp_dir, exist_ok=True)
        print("👁️ Vision Processor initialized")
    
    def take_screenshot(self, save_path: str = None) -> str:
        """Chụp màn hình"""
        try:
            import pyautogui
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(self.temp_dir, f"screenshot_{timestamp}.png")
            
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            return save_path
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return ""
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Phân tích hình ảnh tổng quát"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Cannot load image"}
            
            # Basic analysis
            height, width, channels = image.shape
            
            # Color analysis
            avg_color = np.mean(image, axis=(0, 1))
            
            # Brightness
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)
            
            return {
                "dimensions": {"width": width, "height": height},
                "avg_color_bgr": avg_color.tolist(),
                "brightness": float(brightness),
                "edge_density": float(edge_density),
                "file_path": image_path
            }
        except Exception as e:
            return {"error": str(e)}
    
    def extract_text_ocr(self, image_path: str, lang: str = "vie+eng") -> Dict[str, Any]:
        """Extract text từ hình ảnh bằng OCR"""
        try:
            # Load and preprocess image
            image = Image.open(image_path)
            
            # Enhance image for better OCR
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=lang)
            
            # Get detailed data
            data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
            
            # Filter confident text
            confident_text = []
            for i, conf in enumerate(data['conf']):
                if int(conf) > 30:  # Confidence threshold
                    word = data['text'][i].strip()
                    if word:
                        confident_text.append({
                            "text": word,
                            "confidence": int(conf),
                            "bbox": {
                                "x": data['left'][i],
                                "y": data['top'][i],
                                "width": data['width'][i],
                                "height": data['height'][i]
                            }
                        })
            
            return {
                "full_text": text.strip(),
                "words": confident_text,
                "total_words": len(confident_text),
                "avg_confidence": np.mean([w["confidence"] for w in confident_text]) if confident_text else 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect objects trong hình ảnh (basic version)"""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            objects = []
            for (x, y, w, h) in faces:
                objects.append({
                    "type": "face",
                    "confidence": 0.8,
                    "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}
                })
            
            return objects
        except Exception as e:
            print(f"❌ Object detection error: {e}")
            return []
    
    def analyze_screenshot_for_elements(self, screenshot_path: str) -> Dict[str, Any]:
        """Phân tích screenshot để tìm UI elements"""
        try:
            image = cv2.imread(screenshot_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Find buttons (rectangular shapes)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            ui_elements = []
            for contour in contours:
                # Filter by area
                area = cv2.contourArea(contour)
                if 1000 < area < 50000:  # Reasonable button size
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    # Classify by aspect ratio
                    if 0.3 < aspect_ratio < 3.0:  # Likely button
                        ui_elements.append({
                            "type": "button",
                            "bbox": {"x": x, "y": y, "width": w, "height": h},
                            "area": area,
                            "aspect_ratio": aspect_ratio
                        })
            
            return {
                "ui_elements": ui_elements,
                "total_elements": len(ui_elements)
            }
        except Exception as e:
            return {"error": str(e)}

class VisualQuestionAnswering:
    """Visual Question Answering system"""
    
    def __init__(self, vision_processor: VisionProcessor):
        self.vision = vision_processor
    
    def answer_question(self, image_path: str, question: str) -> Dict[str, Any]:
        """Trả lời câu hỏi về hình ảnh"""
        # Analyze image
        image_analysis = self.vision.analyze_image(image_path)
        ocr_result = self.vision.extract_text_ocr(image_path)
        objects = self.vision.detect_objects(image_path)
        
        # Simple rule-based QA
        question_lower = question.lower()
        
        # Text-related questions
        if any(word in question_lower for word in ["text", "viết", "chữ", "nội dung"]):
            return {
                "answer": f"Tôi tìm thấy văn bản: {ocr_result.get('full_text', 'Không có text')[:200]}",
                "confidence": 0.8,
                "source": "ocr"
            }
        
        # Color questions
        elif any(word in question_lower for word in ["color", "màu", "colour"]):
            avg_color = image_analysis.get("avg_color_bgr", [0, 0, 0])
            dominant_color = self._get_dominant_color_name(avg_color)
            return {
                "answer": f"Màu chủ đạo trong ảnh là {dominant_color}",
                "confidence": 0.7,
                "source": "color_analysis"
            }
        
        # Size/dimension questions
        elif any(word in question_lower for word in ["size", "kích thước", "dimension"]):
            dims = image_analysis.get("dimensions", {})
            return {
                "answer": f"Kích thước ảnh: {dims.get('width', 0)}x{dims.get('height', 0)} pixels",
                "confidence": 0.9,
                "source": "metadata"
            }
        
        # Face questions
        elif any(word in question_lower for word in ["face", "người", "mặt"]):
            face_count = len([obj for obj in objects if obj["type"] == "face"])
            return {
                "answer": f"Tôi tìm thấy {face_count} khuôn mặt trong ảnh",
                "confidence": 0.8,
                "source": "object_detection"
            }
        
        # Brightness questions
        elif any(word in question_lower for word in ["bright", "sáng", "tối", "dark"]):
            brightness = image_analysis.get("brightness", 0)
            if brightness > 150:
                brightness_desc = "sáng"
            elif brightness > 80:
                brightness_desc = "trung bình"
            else:
                brightness_desc = "tối"
            
            return {
                "answer": f"Ảnh có độ sáng {brightness_desc} (giá trị: {brightness:.1f})",
                "confidence": 0.7,
                "source": "brightness_analysis"
            }
        
        # Default response
        return {
            "answer": "Tôi không thể trả lời câu hỏi này về ảnh. Hãy thử hỏi về text, màu sắc, kích thước hoặc độ sáng.",
            "confidence": 0.1,
            "source": "fallback"
        }
    
    def _get_dominant_color_name(self, bgr_color: List[float]) -> str:
        """Chuyển đổi BGR color thành tên màu"""
        b, g, r = bgr_color
        
        # Simple color classification
        if r > g and r > b:
            if r > 150:
                return "đỏ"
            else:
                return "đỏ tối"
        elif g > r and g > b:
            if g > 150:
                return "xanh lá"
            else:
                return "xanh lá tối"
        elif b > r and b > g:
            if b > 150:
                return "xanh dương"
            else:
                return "xanh dương tối"
        else:
            avg = (r + g + b) / 3
            if avg > 200:
                return "trắng"
            elif avg < 50:
                return "đen"
            else:
                return "xám"
    
    def describe_image(self, image_path: str) -> str:
        """Mô tả tổng quát về hình ảnh"""
        analysis = self.vision.analyze_image(image_path)
        ocr = self.vision.extract_text_ocr(image_path)
        objects = self.vision.detect_objects(image_path)
        
        description_parts = []
        
        # Dimensions
        dims = analysis.get("dimensions", {})
        description_parts.append(f"Đây là một hình ảnh có kích thước {dims.get('width', 0)}x{dims.get('height', 0)} pixels")
        
        # Brightness
        brightness = analysis.get("brightness", 0)
        if brightness > 150:
            description_parts.append("Ảnh khá sáng")
        elif brightness < 80:
            description_parts.append("Ảnh khá tối")
        
        # Text content
        if ocr.get("total_words", 0) > 0:
            description_parts.append(f"Có chứa {ocr['total_words']} từ văn bản")
            if ocr["full_text"][:50]:
                description_parts.append(f"Bắt đầu bằng: '{ocr['full_text'][:50]}...'")
        
        # Faces
        face_count = len([obj for obj in objects if obj["type"] == "face"])
        if face_count > 0:
            description_parts.append(f"Có {face_count} khuôn mặt")
        
        return ". ".join(description_parts) + "."