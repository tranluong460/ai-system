"""
Enhanced Computer Vision System với OCR, Object Detection, VQA
"""
import cv2
import numpy as np
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import json
import base64
import pyautogui

# Optional imports for enhanced features
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

class EnhancedVisionProcessor:
    """Enhanced Computer Vision với multiple OCR engines và object detection"""
    
    def __init__(self, data_dir: str = "data/vision"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # OCR engines
        self.ocr_engines = {"tesseract": True}
        
        if EASYOCR_AVAILABLE:
            print("📖 Loading EasyOCR...")
            self.easyocr_reader = easyocr.Reader(['en', 'vi'])
            self.ocr_engines["easyocr"] = True
        else:
            self.easyocr_reader = None
            self.ocr_engines["easyocr"] = False
        
        # Object detection model
        if YOLO_AVAILABLE:
            print("🔍 Loading YOLO model...")
            try:
                self.yolo_model = YOLO('yolov8n.pt')  # nano version for speed
                self.ocr_engines["yolo"] = True
            except:
                self.yolo_model = None
                self.ocr_engines["yolo"] = False
                print("⚠️ Could not load YOLO model")
        else:
            self.yolo_model = None
            self.ocr_engines["yolo"] = False
        
        # Screenshot settings
        pyautogui.FAILSAFE = True
        
        print("👁️ Enhanced Vision Processor ready!")
        print(f"Available engines: {[k for k, v in self.ocr_engines.items() if v]}")
    
    def take_screenshot(self, region: Tuple[int, int, int, int] = None, 
                       save_path: str = None) -> str:
        """Chụp màn hình với region option"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not save_path:
                save_path = os.path.join(self.data_dir, f"screenshot_{timestamp}.png")
            
            if region:
                # Chụp region cụ thể (x, y, width, height)
                screenshot = pyautogui.screenshot(region=region)
            else:
                # Chụp toàn màn hình
                screenshot = pyautogui.screenshot()
            
            screenshot.save(save_path)
            
            return save_path
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return ""
    
    def preprocess_image_for_ocr(self, image_path: str, save_preprocessed: bool = True) -> str:
        """Tiền xử lý ảnh để OCR tốt hơn"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return image_path
            
            # Convert to PIL for better processing
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.5)
            
            # Convert back to OpenCV
            enhanced_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
            
            # Noise reduction
            denoised = cv2.medianBlur(gray, 3)
            
            # Adaptive thresholding
            processed = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)
            
            if save_preprocessed:
                base_name = os.path.splitext(image_path)[0]
                processed_path = f"{base_name}_processed.png"
                cv2.imwrite(processed_path, processed)
                return processed_path
            else:
                # Save to temp
                temp_path = os.path.join(self.data_dir, "temp_processed.png")
                cv2.imwrite(temp_path, processed)
                return temp_path
                
        except Exception as e:
            print(f"❌ Preprocessing error: {e}")
            return image_path
    
    def extract_text_multi_engine(self, image_path: str, 
                                 preprocess: bool = True) -> Dict[str, Any]:
        """Extract text sử dụng multiple OCR engines"""
        results = {"engines_used": [], "results": {}, "best_result": None}
        
        # Preprocess if requested
        if preprocess:
            processed_path = self.preprocess_image_for_ocr(image_path)
        else:
            processed_path = image_path
        
        # Tesseract OCR
        try:
            image = Image.open(processed_path)
            
            # Basic Tesseract
            tesseract_text = pytesseract.image_to_string(image, lang='vie+eng')
            tesseract_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Filter confident words
            confident_words = []
            for i, conf in enumerate(tesseract_data['conf']):
                if int(conf) > 30:
                    word = tesseract_data['text'][i].strip()
                    if word:
                        confident_words.append({
                            "text": word,
                            "confidence": int(conf),
                            "bbox": {
                                "x": tesseract_data['left'][i],
                                "y": tesseract_data['top'][i],
                                "width": tesseract_data['width'][i],
                                "height": tesseract_data['height'][i]
                            }
                        })
            
            results["engines_used"].append("tesseract")
            results["results"]["tesseract"] = {
                "full_text": tesseract_text.strip(),
                "words": confident_words,
                "avg_confidence": np.mean([w["confidence"] for w in confident_words]) if confident_words else 0
            }
            
        except Exception as e:
            print(f"❌ Tesseract error: {e}")
        
        # EasyOCR
        if self.easyocr_reader:
            try:
                easyocr_results = self.easyocr_reader.readtext(processed_path)
                
                easyocr_words = []
                easyocr_text_parts = []
                
                for (bbox, text, confidence) in easyocr_results:
                    if confidence > 0.3:  # 30% confidence threshold
                        easyocr_words.append({
                            "text": text,
                            "confidence": int(confidence * 100),
                            "bbox": {
                                "points": bbox,  # EasyOCR returns 4 corner points
                                "x": int(min([p[0] for p in bbox])),
                                "y": int(min([p[1] for p in bbox])),
                                "width": int(max([p[0] for p in bbox]) - min([p[0] for p in bbox])),
                                "height": int(max([p[1] for p in bbox]) - min([p[1] for p in bbox]))
                            }
                        })
                        easyocr_text_parts.append(text)
                
                results["engines_used"].append("easyocr")
                results["results"]["easyocr"] = {
                    "full_text": " ".join(easyocr_text_parts),
                    "words": easyocr_words,
                    "avg_confidence": np.mean([w["confidence"] for w in easyocr_words]) if easyocr_words else 0
                }
                
            except Exception as e:
                print(f"❌ EasyOCR error: {e}")
        
        # Determine best result
        best_engine = None
        best_confidence = 0
        
        for engine, result in results["results"].items():
            if result["avg_confidence"] > best_confidence:
                best_confidence = result["avg_confidence"]
                best_engine = engine
        
        if best_engine:
            results["best_result"] = {
                "engine": best_engine,
                "confidence": best_confidence,
                **results["results"][best_engine]
            }
        
        return results
    
    def detect_objects_yolo(self, image_path: str, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Object detection với YOLO"""
        if not self.yolo_model:
            return []
        
        try:
            # Run YOLO inference
            results = self.yolo_model(image_path)
            
            objects = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for i, box in enumerate(boxes):
                        confidence = float(box.conf[0])
                        if confidence >= confidence_threshold:
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            
                            # Get class name
                            class_id = int(box.cls[0])
                            class_name = self.yolo_model.names[class_id]
                            
                            objects.append({
                                "class": class_name,
                                "confidence": confidence,
                                "bbox": {
                                    "x": int(x1),
                                    "y": int(y1),
                                    "width": int(x2 - x1),
                                    "height": int(y2 - y1)
                                }
                            })
            
            return objects
            
        except Exception as e:
            print(f"❌ YOLO detection error: {e}")
            return []
    
    def analyze_screenshot_ui(self, screenshot_path: str) -> Dict[str, Any]:
        """Phân tích UI elements trong screenshot"""
        try:
            image = cv2.imread(screenshot_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Find UI elements using contours
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            ui_elements = {
                "buttons": [],
                "text_areas": [],
                "windows": [],
                "icons": []
            }
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by area
                if area < 500:  # Too small
                    continue
                if area > 100000:  # Too large (probably background)
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                element_info = {
                    "bbox": {"x": x, "y": y, "width": w, "height": h},
                    "area": area,
                    "aspect_ratio": aspect_ratio
                }
                
                # Classify based on size and aspect ratio
                if 1000 < area < 20000:
                    if 0.3 < aspect_ratio < 4.0:
                        ui_elements["buttons"].append(element_info)
                    elif aspect_ratio > 4.0:
                        ui_elements["text_areas"].append(element_info)
                elif area > 20000:
                    ui_elements["windows"].append(element_info)
                elif 500 < area < 2000 and 0.8 < aspect_ratio < 1.2:
                    ui_elements["icons"].append(element_info)
            
            return {
                "ui_elements": ui_elements,
                "total_elements": sum(len(elements) for elements in ui_elements.values()),
                "image_size": {"width": image.shape[1], "height": image.shape[0]}
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def find_text_on_screen(self, target_text: str, screenshot_path: str = None) -> List[Dict[str, Any]]:
        """Tìm text trên màn hình và trả về vị trí"""
        if not screenshot_path:
            screenshot_path = self.take_screenshot()
        
        if not screenshot_path:
            return []
        
        # Extract text with positions
        ocr_results = self.extract_text_multi_engine(screenshot_path)
        
        matches = []
        target_lower = target_text.lower()
        
        # Search in best result
        if ocr_results["best_result"]:
            words = ocr_results["best_result"]["words"]
            
            for word in words:
                if target_lower in word["text"].lower():
                    matches.append({
                        "text": word["text"],
                        "bbox": word["bbox"],
                        "confidence": word["confidence"],
                        "match_type": "exact" if target_lower == word["text"].lower() else "partial"
                    })
        
        return matches
    
    def click_on_text(self, target_text: str, screenshot_path: str = None) -> bool:
        """Click vào text trên màn hình"""
        matches = self.find_text_on_screen(target_text, screenshot_path)
        
        if not matches:
            print(f"❌ Text '{target_text}' not found on screen")
            return False
        
        # Click on first match
        match = matches[0]
        bbox = match["bbox"]
        
        # Calculate center point
        center_x = bbox["x"] + bbox["width"] // 2
        center_y = bbox["y"] + bbox["height"] // 2
        
        try:
            pyautogui.click(center_x, center_y)
            print(f"✅ Clicked on '{match['text']}' at ({center_x}, {center_y})")
            return True
        except Exception as e:
            print(f"❌ Click error: {e}")
            return False
    
    def extract_table_from_image(self, image_path: str) -> List[List[str]]:
        """Extract table data từ ảnh"""
        try:
            # Get OCR results with bounding boxes
            ocr_results = self.extract_text_multi_engine(image_path)
            
            if not ocr_results["best_result"]:
                return []
            
            words = ocr_results["best_result"]["words"]
            
            # Group words by rows based on Y coordinate
            rows = {}
            for word in words:
                y = word["bbox"]["y"]
                row_key = y // 20  # Group by 20-pixel rows
                
                if row_key not in rows:
                    rows[row_key] = []
                
                rows[row_key].append(word)
            
            # Sort rows by Y coordinate
            sorted_rows = sorted(rows.items())
            
            # Extract table data
            table_data = []
            for _, row_words in sorted_rows:
                # Sort words in row by X coordinate
                row_words.sort(key=lambda w: w["bbox"]["x"])
                
                # Extract text
                row_text = [word["text"] for word in row_words]
                if row_text:  # Skip empty rows
                    table_data.append(row_text)
            
            return table_data
            
        except Exception as e:
            print(f"❌ Table extraction error: {e}")
            return []

class VisualQuestionAnswering:
    """Enhanced Visual Question Answering"""
    
    def __init__(self, vision_processor: EnhancedVisionProcessor):
        self.vision = vision_processor
        
        # Extended knowledge base
        self.visual_knowledge = {
            "colors": {
                "red": ["đỏ", "red", "crimson", "scarlet"],
                "blue": ["xanh dương", "blue", "navy", "azure"],
                "green": ["xanh lá", "green", "emerald"],
                "yellow": ["vàng", "yellow", "gold"],
                "black": ["đen", "black"],
                "white": ["trắng", "white"],
                "gray": ["xám", "grey", "gray"]
            },
            "objects": {
                "person": ["người", "person", "human"],
                "car": ["xe", "car", "vehicle", "ô tô"],
                "computer": ["máy tính", "computer", "laptop"],
                "phone": ["điện thoại", "phone", "mobile"]
            }
        }
    
    def answer_question(self, image_path: str, question: str) -> Dict[str, Any]:
        """Trả lời câu hỏi về hình ảnh với enhanced analysis"""
        question_lower = question.lower()
        
        # Analyze image comprehensively
        image_analysis = self.vision.analyze_image(image_path) if hasattr(self.vision, 'analyze_image') else {}
        ocr_result = self.vision.extract_text_multi_engine(image_path)
        objects = self.vision.detect_objects_yolo(image_path)
        ui_analysis = self.vision.analyze_screenshot_ui(image_path)
        
        # Enhanced question answering
        
        # Text-related questions
        if any(word in question_lower for word in ["text", "viết", "chữ", "nội dung", "đọc", "read"]):
            if ocr_result["best_result"]:
                text = ocr_result["best_result"]["full_text"]
                word_count = len(ocr_result["best_result"]["words"])
                confidence = ocr_result["best_result"]["confidence"]
                
                return {
                    "answer": f"Tôi tìm thấy {word_count} từ với độ tin cậy {confidence:.1f}%. Nội dung: {text[:300]}{'...' if len(text) > 300 else ''}",
                    "confidence": confidence / 100,
                    "source": "multi_engine_ocr",
                    "details": {"word_count": word_count, "engines_used": ocr_result["engines_used"]}
                }
        
        # Object counting questions
        elif any(word in question_lower for word in ["bao nhiêu", "how many", "count", "đếm"]):
            if objects:
                object_counts = {}
                for obj in objects:
                    class_name = obj["class"]
                    object_counts[class_name] = object_counts.get(class_name, 0) + 1
                
                count_text = ", ".join([f"{count} {obj}" for obj, count in object_counts.items()])
                return {
                    "answer": f"Tôi đếm được: {count_text}",
                    "confidence": 0.8,
                    "source": "yolo_detection",
                    "details": object_counts
                }
        
        # UI-related questions
        elif any(word in question_lower for word in ["button", "nút", "click", "interface", "ui"]):
            ui_elements = ui_analysis.get("ui_elements", {})
            button_count = len(ui_elements.get("buttons", []))
            
            return {
                "answer": f"Tôi tìm thấy {button_count} nút bấm và {ui_analysis.get('total_elements', 0)} UI elements tổng cộng",
                "confidence": 0.7,
                "source": "ui_analysis",
                "details": ui_elements
            }
        
        # Object detection questions
        elif any(word in question_lower for word in ["object", "đồ vật", "detect", "nhận diện"]):
            if objects:
                unique_objects = list(set([obj["class"] for obj in objects]))
                return {
                    "answer": f"Tôi nhận diện được: {', '.join(unique_objects)}",
                    "confidence": 0.8,
                    "source": "yolo_detection",
                    "details": {"objects": objects, "unique_classes": unique_objects}
                }
        
        # Table extraction questions
        elif any(word in question_lower for word in ["table", "bảng", "data", "dữ liệu"]):
            table_data = self.vision.extract_table_from_image(image_path)
            if table_data:
                return {
                    "answer": f"Tôi tìm thấy bảng có {len(table_data)} hàng. Hàng đầu: {table_data[0] if table_data else 'N/A'}",
                    "confidence": 0.7,
                    "source": "table_extraction",
                    "details": {"table_data": table_data[:5]}  # First 5 rows only
                }
        
        # Size/dimension questions
        elif any(word in question_lower for word in ["size", "kích thước", "dimension", "lớn"]):
            dims = image_analysis.get("dimensions", {}) or ui_analysis.get("image_size", {})
            return {
                "answer": f"Kích thước ảnh: {dims.get('width', 0)}x{dims.get('height', 0)} pixels",
                "confidence": 0.9,
                "source": "image_metadata"
            }
        
        # Quality assessment
        elif any(word in question_lower for word in ["quality", "chất lượng", "clear", "blur"]):
            # Simple quality assessment based on OCR confidence
            if ocr_result["best_result"]:
                conf = ocr_result["best_result"]["confidence"]
                if conf > 80:
                    quality = "tốt"
                elif conf > 60:
                    quality = "trung bình"
                else:
                    quality = "kém"
                
                return {
                    "answer": f"Chất lượng ảnh: {quality} (OCR confidence: {conf:.1f}%)",
                    "confidence": 0.7,
                    "source": "ocr_confidence_analysis"
                }
        
        # Comprehensive description
        elif any(word in question_lower for word in ["describe", "mô tả", "what", "gì"]):
            description_parts = []
            
            # Add image size
            dims = image_analysis.get("dimensions", {}) or ui_analysis.get("image_size", {})
            description_parts.append(f"Ảnh {dims.get('width', 0)}x{dims.get('height', 0)} pixels")
            
            # Add text content
            if ocr_result["best_result"] and ocr_result["best_result"]["words"]:
                word_count = len(ocr_result["best_result"]["words"])
                description_parts.append(f"có {word_count} từ văn bản")
            
            # Add objects
            if objects:
                unique_objects = list(set([obj["class"] for obj in objects]))
                description_parts.append(f"chứa: {', '.join(unique_objects[:3])}")
            
            # Add UI elements
            if ui_analysis.get("total_elements", 0) > 0:
                description_parts.append(f"có {ui_analysis['total_elements']} UI elements")
            
            description = ". ".join(description_parts) + "."
            
            return {
                "answer": description,
                "confidence": 0.8,
                "source": "comprehensive_analysis"
            }
        
        # Default fallback
        return {
            "answer": "Tôi đã phân tích ảnh nhưng không thể trả lời câu hỏi cụ thể này. Hãy thử hỏi về text, objects, UI elements, kích thước hoặc chất lượng ảnh.",
            "confidence": 0.1,
            "source": "fallback",
            "suggestions": [
                "Có text nào trong ảnh?",
                "Có bao nhiêu objects?", 
                "Mô tả ảnh này",
                "Kích thước ảnh là bao nhiêu?"
            ]
        }