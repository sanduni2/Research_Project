# 🐔 Integrated Farm System - Complete MERN Stack Application

**Poultry Farm Management System with AI/ML Integration**

A comprehensive web and mobile application for chicken feed optimization and growth prediction using Machine Learning.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Features](#-features)
3. [Technology Stack](#-technology-stack)
4. [Project Structure](#-project-structure)
5. [Prerequisites](#-prerequisites)
6. [Installation Guide](#-installation-guide)
7. [Running the Application](#-running-the-application)
8. [API Documentation](#-api-documentation)
9. [ML Models](#-ml-models)
10. [Screenshots](#-screenshots)
11. [Troubleshooting](#-troubleshooting)

---

## 🎯 Project Overview

This system helps poultry farmers optimize chicken feed and predict growth using AI/ML models. The application consists of three main steps:

### **Step 1: Flock Profile Creation**
Create and manage chicken flocks with detailed information (name, breed, count, age).

### **Step 2: Growth Prediction**
- Predict chicken weight based on age using Linear Regression (77% accuracy)
- Detect feed consumption percentage (0%, 25%, 50%, 100%) from images using ResNet50
- Compare actual vs predicted weight
- Get personalized recommendations

### **Step 3: Feed Optimization**
- Generate weekly feed plans based on growth stage
- Calculate feed quantities per chicken and total
- Get ingredient breakdown (corn, soybean, wheat, vitamins, minerals)
- Receive tailored recommendations

---

## ✨ Features

### 🐓 Flock Management
- Create multiple flocks with unique profiles
- Track flock age, count, and breed
- Update flock information
- View historical data

### 📊 Growth Prediction
- **AI-Powered Weight Prediction**: Linear Regression model (R² = 0.7703)
- **Optional Weight Input**: Compare actual vs predicted
- **Image Classification**: ResNet50 CNN for feed consumption detection
- **Real-time Analysis**: Instant feedback and recommendations

### 🌾 Feed Optimization
- **Stage-Based Planning**: Starter (0-6 weeks), Grower (7-18 weeks), Layer (19+ weeks)
- **Nutrition Requirements**: Protein, energy, calcium, phosphorus
- **Feed Calculations**: Daily and weekly quantities
- **Ingredient Mix**: Optimal feed composition
- **Expert Recommendations**: Tailored advice for each stage

### 📱 Mobile-First Design
- React Native cross-platform app
- Beautiful, intuitive UI
- Camera integration for image upload
- Offline-ready architecture

---

## 🛠 Technology Stack

### **Frontend (Mobile)**
- React Native with Expo
- React Navigation
- Axios for API calls
- Expo Image Picker

### **Backend (API Server)**
- Node.js with Express
- MongoDB (Mongoose ODM)
- Multer for file uploads
- JWT authentication (optional)

### **ML Service (Python)**
- Flask REST API
- TensorFlow/Keras (ResNet50)
- Scikit-learn (Linear Regression)
- NumPy, Pillow

### **Database**
- MongoDB (NoSQL)
- Collections: flocks, growthrecords, feedplans

---

## 📁 Project Structure

```
Research/
├── data_anaysis/                    # ML Models & Data
│   ├── models/
│   │   ├── weight_prediction_linear_regression.pkl
│   │   ├── weight_prediction_scaler.pkl
│   │   └── resnet50/
│   │       └── best_model.h5
│   ├── data/
│   │   ├── chickweight_preprocessed.csv
│   │   └── poultry_farm_dataset_preprocessed.csv
│   └── notebooks/
│
├── Integrated-Farm-System-Backend/   # Node.js Backend
│   ├── server.js
│   ├── models/
│   │   ├── Flock.js
│   │   ├── GrowthRecord.js
│   │   └── FeedPlan.js
│   ├── routes/
│   │   ├── flockRoutes.js
│   │   ├── predictionRoutes.js
│   │   └── feedPlanRoutes.js
│   ├── ml_service/
│   │   ├── app.py                   # Flask ML API
│   │   └── requirements.txt
│   └── uploads/
│
└── Integrated-Farm-System-Frontend/  # React Native App
    ├── App.js
    ├── src/
    │   ├── screens/
    │   │   ├── FlockCreationScreen.js
    │   │   ├── GrowthPredictionScreen.js
    │   │   └── FeedOptimizationScreen.js
    │   ├── navigation/
    │   │   └── AppNavigator.js
    │   └── config/
    │       └── apiConfig.js
    └── package.json
```

---

## ✅ Prerequisites

### System Requirements
- **Node.js**: v16 or higher
- **Python**: 3.8 or higher
- **MongoDB**: v5 or higher
- **Expo CLI**: Latest version

### Development Tools
- Visual Studio Code (recommended)
- Android Studio / Xcode (for mobile development)
- Postman (for API testing)
- MongoDB Compass (optional, for database GUI)

---

## 🚀 Installation Guide

### 1. Clone Repository
```bash
cd Desktop/Research
# (Already cloned from GitHub)
```

### 2. Install Backend Dependencies
```bash
cd Integrated-Farm-System-Backend
npm install
```

### 3. Install Frontend Dependencies
```bash
cd Integrated-Farm-System-Frontend
npm install
```

### 4. Install Python ML Service Dependencies
```bash
cd Integrated-Farm-System-Backend/ml_service
pip install -r requirements.txt
```

### 5. Setup MongoDB
Start MongoDB service:
```bash
# Windows (as service)
net start MongoDB

# Or run manually
mongod
```

### 6. Configure Environment

**Backend (.env)**
```
PORT=3000
MONGODB_URI=mongodb://localhost:27017/poultry_farm
ML_SERVICE_URL=http://localhost:5000
```

**Frontend (src/config/apiConfig.js)**
```javascript
// For development
export const API_URL = 'http://localhost:3000/api';

// For physical device (use your computer's IP)
export const API_URL = 'http://192.168.1.100:3000/api';
```

---

## 🏃 Running the Application

### Option 1: Run Everything Separately

#### Terminal 1: Start MongoDB
```bash
mongod
```

#### Terminal 2: Start ML Service (Flask)
```bash
cd Integrated-Farm-System-Backend/ml_service
python app.py
```
✅ ML Service running on `http://localhost:5000`

#### Terminal 3: Start Backend API (Node.js)
```bash
cd Integrated-Farm-System-Backend
npm start
```
✅ Backend API running on `http://localhost:3000`

#### Terminal 4: Start Frontend (React Native)
```bash
cd Integrated-Farm-System-Frontend
npm start
```
✅ Expo Dev Server running
- Press `a` for Android
- Press `i` for iOS
- Scan QR code with Expo Go app

### Option 2: Run with PM2 (Production)

```bash
# Install PM2
npm install -g pm2

# Start all services
pm2 start Integrated-Farm-System-Backend/ml_service/app.py --name ml-service --interpreter python
pm2 start Integrated-Farm-System-Backend/server.js --name backend-api
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:3000/api
```

### Endpoints

#### **Flock Management**
```http
POST   /flocks              # Create flock
GET    /flocks              # Get all flocks
GET    /flocks/:id          # Get single flock
PUT    /flocks/:id          # Update flock
DELETE /flocks/:id          # Delete flock
GET    /flocks/:id/history  # Get flock history
```

#### **Growth Prediction**
```http
POST   /predictions/growth              # Predict with image
GET    /predictions/growth/:flockId/latest  # Get latest prediction
```

#### **Feed Plans**
```http
POST   /feed-plans/generate          # Generate feed plan
GET    /feed-plans/:flockId          # Get all plans
GET    /feed-plans/:flockId/latest   # Get latest plan
```

### Example Request: Create Flock
```bash
curl -X POST http://localhost:3000/api/flocks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Flock Alpha",
    "breed": "Rhode Island Red",
    "initialCount": 100,
    "ageInWeeks": 4
  }'
```

### Example Request: Predict Growth (with Image)
```bash
curl -X POST http://localhost:3000/api/predictions/growth \
  -F "flockId=abc123..." \
  -F "actualWeight=450" \
  -F "feedType=Starter Feed" \
  -F "feedImage=@feed_plate.jpg"
```

---

## 🤖 ML Models

### 1. Weight Prediction Model
**Type**: Linear Regression with Polynomial Features

**Performance**:
- R² Score: 0.7703 (77% accuracy)
- RMSE: 34.19 grams
- MAE: 20.46 grams

**Features**:
- Age in days
- Age² (squared)
- Age³ (cubic)

**Usage**:
```python
POST /api/predict/weight
{
  "age": 35  # Age in days
}

Response:
{
  "success": true,
  "predicted_weight": 430.5,
  "unit": "grams"
}
```

### 2. Feed Consumption Classification (ResNet50)
**Type**: Convolutional Neural Network (Transfer Learning)

**Classes**: 0%, 25%, 50%, 100% feed consumption

**Input**: RGB image (224x224 pixels)

**Usage**:
```python
POST /api/predict/feed-consumption
Content-Type: multipart/form-data
image: [file]

Response:
{
  "success": true,
  "predicted_percentage": 50,
  "confidence": 87.5
}
```

---

## 📱 Screenshots

### Mobile App Flow

**Step 1: Flock Creation**
- Clean form with breed selector
- Input validation
- Professional green theme

**Step 2: Growth Prediction**
- Flock details card
- Image upload (camera/gallery)
- Weight comparison
- Feed consumption analysis
- Recommendations

**Step 3: Feed Optimization**
- Growth stage indicator
- Nutrition breakdown
- Feed quantities
- Visual ingredient bars
- Expert recommendations

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Backend Cannot Connect to ML Service
```
Error: ML Service is not available
```
**Solution**: Ensure ML service is running on port 5000
```bash
cd Integrated-Farm-System-Backend/ml_service
python app.py
```

#### 2. Frontend Cannot Connect to Backend
```
Network Error / ECONNREFUSED
```
**Solution**: 
- Check if backend is running on port 3000
- Update API_URL in `src/config/apiConfig.js`
- For physical devices, use computer's IP address

#### 3. MongoDB Connection Error
```
MongoNetworkError: connect ECONNREFUSED 127.0.0.1:27017
```
**Solution**: Start MongoDB service
```bash
net start MongoDB  # Windows
brew services start mongodb-community  # Mac
```

#### 4. Image Upload Fails
```
Error uploading image
```
**Solution**:
- Check file size (max 10MB)
- Ensure file format is JPG/JPEG/PNG
- Check `uploads/feed-images` directory exists
- Verify multer configuration

#### 5. Model Not Found
```
Error loading weight model
```
**Solution**:
- Verify models exist in `data_anaysis/models/`
- Check file paths in `ml_service/app.py`
- Ensure models were trained successfully

#### 6. Expo Cannot Start
```
Error: Metro bundler failed to start
```
**Solution**:
```bash
# Clear cache
npm start -- --reset-cache

# Or
expo start -c
```

### Get Your Computer's IP Address

**Windows**:
```bash
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

**Mac/Linux**:
```bash
ifconfig
# or
ip addr show
```

---

## 📊 Database Schema

### Flocks Collection
```javascript
{
  name: String,
  breed: String,
  initialCount: Number,
  currentCount: Number,
  ageInWeeks: Number,
  createdAt: Date,
  isActive: Boolean
}
```

### GrowthRecords Collection
```javascript
{
  flock: ObjectId,
  weekNumber: Number,
  ageInDays: Number,
  actualWeight: Number,
  predictedWeight: Number,
  feedConsumedPercentage: Number,
  feedType: String,
  imageUrl: String,
  recommendation: String,
  growthStatus: String
}
```

### FeedPlans Collection
```javascript
{
  flock: ObjectId,
  weekNumber: Number,
  growthStage: String,
  nutritionPlan: {
    protein: Number,
    energy: Number,
    calcium: Number,
    phosphorus: Number
  },
  ingredients: {
    corn: Number,
    soybeanMeal: Number,
    wheat: Number,
    vitamins: Number,
    minerals: Number
  },
  recommendations: [String]
}
```

---

## 🎓 Growth Stages Reference

### Starter Stage (0-6 weeks)
- **Protein**: 20%
- **Energy**: 3000 kcal/kg
- **Feed**: 54% corn, 34% soybean, 7% wheat
- **Focus**: Rapid growth and development

### Grower Stage (7-18 weeks)
- **Protein**: 16%
- **Energy**: 2900 kcal/kg
- **Feed**: 60% corn, 26% soybean, 9% wheat
- **Focus**: Sustained growth and body development

### Layer Stage (19+ weeks)
- **Protein**: 18%
- **Energy**: 2850 kcal/kg
- **Calcium**: 3.5% (for eggshells)
- **Feed**: 58% corn, 24% soybean, 8% wheat
- **Focus**: Egg production and shell quality

---

## 📚 Additional Resources

- [Backend API Documentation](Integrated-Farm-System-Backend/README_API.md)
- [Frontend Documentation](Integrated-Farm-System-Frontend/README_FRONTEND.md)
- [Model Training Notebooks](data_anaysis/notebooks/)
- [Model Performance Summary](data_anaysis/MODEL_RESULTS_SUMMARY.md)

---

## 👥 Team & Credits

**Research Project - Final Year**

Built with ❤️ using:
- MERN Stack (MongoDB, Express, React Native, Node.js)
- Python Machine Learning (TensorFlow, Scikit-learn)
- Flask RESTful API

---

## 📄 License

This project is for educational purposes as part of a final year research project.

---

## 🙏 Acknowledgments

- Chicken weight dataset: ChickWeight (R datasets)
- Poultry farm dataset: Kaggle
- ResNet50 model: TensorFlow/Keras pre-trained weights
- Icons: Emoji icons for UI elements

---

## 📞 Support

For issues and questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review API documentation
3. Check MongoDB logs
4. Verify all services are running

---

**Happy Farming! 🐔🌾**
