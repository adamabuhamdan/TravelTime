# 🛫 TravelTime + Artifact AI

### **Flutter Mobile App with AI-Powered Artifact Analysis**

[![Flutter](https://img.shields.io/badge/Flutter-3.32.6-02569B?logo=flutter)](https://flutter.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python)](https://python.org)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Vision-8E75B2?logo=google)](https://ai.google.dev)

---

## 📘 Overview

**TravelTime** is a comprehensive Flutter mobile application that seamlessly integrates traditional travel management with cutting-edge AI artifact analysis capabilities.

### ✈️ **TravelTime Core Features**

- 📸 Image capture and storage management
- 🗺️ Trip planning and note-taking
- 🌐 Bilingual support (Arabic/English)
- 📱 Android 14 compatibility
- 🔐 Robust permission handling

### 🏺 **Artifact AI Module**

An intelligent analysis system that provides:

- ✅ **Artifact Image Analysis** - Deep learning-powered artifact recognition
- 🔍 **Detailed Artifact Information** - Powered by **Gemini 2.5 Vision API**
- 🎨 **Image Enhancement** - Using **WaveSpeed + Qwen Image Editor**
- 📝 **Museum-Quality Arabic Descriptions** - Professional archaeological documentation
- 🎭 **3D Rendering Prompts** - Ready-to-use prompts for 3D modeling
- ☁️ **Cloud Storage Integration** - Automatic upload to **Cloudinary CDN**
- 📊 **Structured JSON Responses** - Clean, well-formatted API output

---

## ⚙️ Technology Stack

### **Frontend**

| Technology | Version | Purpose |
|------------|---------|---------|
| Flutter | 3.32.6 | Cross-platform mobile framework |
| Dart | 3.8 | Programming language |
| Dio | Latest | HTTP client for API communication |
| Provider | Latest | State management solution |
| Image Picker | Latest | Camera and gallery integration |
| Permission Handler | Latest | Runtime permissions management |
| Material 3 | Latest | Modern UI components |

### **Backend**

| Technology | Purpose |
|------------|---------|
| FastAPI | High-performance REST API framework |
| Uvicorn | ASGI web server |
| Python | 3.10 |
| Google Gemini 2.5 Vision | AI-powered image analysis |
| WaveSpeed API | Image enhancement and editing |
| Qwen Image Editor | Advanced image processing |
| Cloudinary SDK | Cloud-based media management |

---

## 📡 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Flutter Mobile App                      │
├─────────────────────────────────────────────────────────────┤
│  1. User selects artifact image                             │
│  2. Image Picker captures/selects photo                     │
│  3. Prepare multipart FormData                              │
│  4. Send POST request to FastAPI backend                    │
│  5. Display results (Description + Enhanced Image + 3D)     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Service                   │
├─────────────────────────────────────────────────────────────┤
│  1. Receive image file upload                               │
│  2. Analyze artifact using Gemini 2.5 Vision                │
│  3. Enhance image quality (WaveSpeed/Qwen)                  │
│  4. Generate Arabic description + 3D prompt                 │
│  5. Upload processed image to Cloudinary                    │
│  6. Return structured JSON response                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Flutter SDK 3.32.6 or higher
- Python 3.10 or higher
- Android Studio / VS Code
- Physical Android device or emulator
- API Keys:
  - Google Gemini API Key
  - WaveSpeed API Key
  - Cloudinary Account (Cloud Name, API Key, Secret)

---

## 🔧 Installation Guide

### **1️⃣ Backend Setup (FastAPI)**

#### Clone the Repository

```bash
git clone <your-repository-url>
cd backend
```

#### Create Virtual Environment

Using Conda:
```bash
conda create -n artifact-ai python=3.10
conda activate artifact-ai
```

Or using venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the backend directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
WAVESPEED_API_KEY=your_wavespeed_api_key_here
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
```

#### Start the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

#### Verify Installation

Access the interactive API documentation:
- Swagger UI: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
- ReDoc: [http://127.0.0.1:8080/redoc](http://127.0.0.1:8080/redoc)

---

### **2️⃣ Frontend Setup (Flutter)**

#### Navigate to Frontend Directory

```bash
cd frontend
```

#### Install Dependencies

```bash
flutter pub get
```

#### Run on Device/Emulator

```bash
flutter run
```

---

## 📱 Connecting Physical Device to Local Backend

When testing on a physical Android device:

### Step 1: Verify Device Connection

```bash
adb devices
```

You should see your device listed.

### Step 2: Port Forwarding

Enable the device to access your local backend:

```bash
adb reverse tcp:8080 tcp:8080
```

### Step 3: Launch Application

```bash
flutter run
```

The app will now communicate with your local FastAPI server at `http://localhost:8080`.

---

## 🔐 Android Permissions Configuration

For Android 14+ compatibility, ensure your `AndroidManifest.xml` includes:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    
    <!-- Camera and Image Permissions -->
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"
        android:maxSdkVersion="32"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
        android:maxSdkVersion="32"/>
    
    <application>
        <!-- Your application configuration -->
    </application>
</manifest>
```

---

## 🧪 API Documentation

### Endpoint: Artifact Analysis Pipeline

**URL:** `POST /artifact-3d-pipeline-wavespeed`

**Content-Type:** `multipart/form-data`

**Request:**

```dart
// Flutter Implementation (using Dio)
final formData = FormData.fromMap({
  'file': await MultipartFile.fromFile(
    imagePath,
    filename: 'artifact.jpg',
  ),
});

final response = await dio.post(
  '/artifact-3d-pipeline-wavespeed',
  data: formData,
  options: Options(
    headers: {'Content-Type': 'multipart/form-data'},
  ),
);
```

**Python Backend Implementation:**

```python
from fastapi import FastAPI, UploadFile, File
from services.gemini_service import analyze_artifact
from services.image_service import enhance_image
from services.cloudinary_service import upload_to_cloud

app = FastAPI()

@app.post("/artifact-3d-pipeline-wavespeed")
async def process_artifact(file: UploadFile = File(...)):
    # Read image bytes
    image_bytes = await file.read()
    
    # Step 1: Analyze with Gemini Vision
    analysis = await analyze_artifact(image_bytes)
    
    # Step 2: Enhance image quality
    enhanced_image = await enhance_image(image_bytes)
    
    # Step 3: Upload to Cloudinary
    cloudinary_url = await upload_to_cloud(enhanced_image)
    
    # Step 4: Return structured response
    return {
        "arabic_definition": analysis.arabic_description,
        "image_url": cloudinary_url,
        "prompt_3d": analysis.rendering_prompt,
        "metadata": analysis.artifact_metadata
    }
```

---

## 📊 Response Format

### Sample JSON Response

```json
{
  "arabic_definition": "قطعة فخارية أثرية من العصر البرونزي المبكر (3000-2000 ق.م)، تتميز بزخارف هندسية منقوشة يدوياً. تظهر القطعة علامات استخدام يومي مما يشير إلى أنها كانت جزءاً من الأواني المنزلية. المادة المستخدمة هي طين محلي محروق بدرجة حرارة متوسطة.",
  
  "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/artifacts/artifact_enhanced.jpg",
  
  "prompt_3d": "Ultra-realistic 3D render of an ancient Bronze Age pottery artifact, multi-angle view (front, side, top), photogrammetry-ready, 8K resolution, museum-quality lighting, geometric patterns clearly visible, weathered texture with authentic aging, PBR materials, Blender-compatible",
  
  "metadata": {
    "confidence_score": 0.92,
    "detected_period": "Early Bronze Age",
    "estimated_year_range": "3000-2000 BCE",
    "material": "Fired clay",
    "condition": "Good with minor wear",
    "cultural_context": "Mesopotamian"
  }
}
```

---



## 🏆 Key Features & Differentiators

### What Makes This Project Stand Out

1. **🤖 Multi-AI Integration**
   - Seamlessly combines Gemini 2.5 Vision, WaveSpeed, and Qwen
   - Real AI pipeline, not just API calls

2. **🎯 Real Archaeological Analysis**
   - Museum-quality artifact descriptions
   - Goes beyond basic OCR or image recognition
   - Provides historical context and metadata

3. **⚡ High Performance**
   - FastAPI backend for sub-second response times
   - Optimized image processing pipeline
   - Efficient state management with Provider

4. **🌐 Production-Ready Architecture**
   - Clean separation of concerns
   - Scalable microservices design
   - Comprehensive error handling
   - API documentation included

5. **📱 Modern Mobile Development**
   - Material 3 design system
   - Responsive UI/UX
   - Proper permission handling
   - Cross-platform compatibility

6. **☁️ Cloud Integration**
   - Cloudinary CDN for fast image delivery
   - Secure API key management
   - Environment-based configuration

---

## 🎓 Use Cases

This project is ideal for:

- 📚 **Academic Projects** - Demonstrates advanced mobile + AI integration
- 💼 **Portfolio Showcase** - Highlights full-stack development skills
- 🏅 **Hackathons** - Complete, deployable solution with wow factor
- 🎨 **Museum Applications** - Real-world archaeological documentation
- 🚀 **Startup MVP** - Foundation for artifact authentication platforms

---

## 🔮 Future Enhancements

Potential features for expansion:

- [ ] User authentication and profiles
- [ ] Artifact database with search functionality
- [ ] Social sharing of discoveries
- [ ] Offline mode with local AI models
- [ ] AR visualization of 3D models
- [ ] Multi-language support (expand beyond Arabic/English)
- [ ] Integration with museum databases
- [ ] Blockchain-based artifact verification
- [ ] Community-driven artifact identification
- [ ] Export to 3D modeling software (Blender, Maya)

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Flutter Tests

```bash
cd frontend
flutter test
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Matthew Nashtec**  
AI Engineer · Flutter Developer · Backend Architect

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?logo=linkedin)]([https://linkedin.com/in/yourprofile](https://www.linkedin.com/in/adam-abu-hamdan-a14993279/))
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?logo=github)]([https://github.com/yourprofile](https://github.com/adamabuhamdan))
[![Email](https://img.shields.io/badge/Email-Contact-D14836?logo=gmail)](abuhamdanadam15@gmail.com)

---

## 🙏 Acknowledgments

- Google Gemini Team for the Vision API
- WaveSpeed for image enhancement capabilities
- Cloudinary for reliable cloud storage
- Flutter team for the excellent framework
- FastAPI community for comprehensive documentation

---

## 📞 Support

For questions, issues, or suggestions:

- 📧 Email: abuhamdanadam15@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourrepo/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourrepo/discussions)

---

<div align="center">

**⭐ If you find this project helpful, please consider giving it a star! ⭐**

Made with ❤️ and ☕ by Adam Abu Hamdan

</div>
