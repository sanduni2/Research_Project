# Integrated Farm System - Backend API

Complete backend API for Poultry Farm Management System with ML integration.

## 🎯 Features

- **Flock Management**: Create and manage chicken flocks with detailed profiles
- **Growth Prediction**: Predict chicken weight using trained ML models (77% accuracy)
- **Image Classification**: Detect feed consumption percentage (0%, 25%, 50%, 100%) using ResNet50
- **Feed Optimization**: Generate weekly feed plans based on age and weight
- **Historical Tracking**: View growth history and feed consumption patterns

## 📋 Prerequisites

- Node.js (v16+)
- MongoDB (v5+)
- Python (3.8+) for ML service

## 🚀 Installation & Setup

### 1. Install Node.js Dependencies

```bash
cd Integrated-Farm-System-Backend
npm install
```

### 2. Install Python ML Service Dependencies

```bash
cd ml_service
pip install -r requirements.txt
```

### 3. Setup MongoDB

Make sure MongoDB is running on your system:
```bash
# Windows (if installed as service)
net start MongoDB

# Or run manually
mongod
```

### 4. Configure Environment

Edit `.env` file and update if needed:
```
PORT=3000
MONGODB_URI=mongodb://localhost:27017/poultry_farm
ML_SERVICE_URL=http://localhost:5000
```

## 🏃 Running the Application

You need to run TWO services:

### Terminal 1: Start ML Service (Python Flask)
```bash
cd Integrated-Farm-System-Backend\ml_service
python app.py
```

ML Service will run on: `http://localhost:5000`

### Terminal 2: Start Backend API (Node.js Express)
```bash
cd Integrated-Farm-System-Backend
npm start
```

Backend API will run on: `http://localhost:3000`

## 📡 API Endpoints

### Health Check
```http
GET /api/health
```

### Flock Management

**Create Flock**
```http
POST /api/flocks
Content-Type: application/json

{
  "name": "Flock Alpha",
  "breed": "Rhode Island Red",
  "initialCount": 100,
  "ageInWeeks": 4,
  "notes": "Healthy chicks"
}
```

**Get All Flocks**
```http
GET /api/flocks
```

**Get Single Flock**
```http
GET /api/flocks/:id
```

**Get Flock History**
```http
GET /api/flocks/:id/history
```

**Update Flock**
```http
PUT /api/flocks/:id
Content-Type: application/json

{
  "currentCount": 98,
  "notes": "Updated notes"
}
```

**Delete Flock**
```http
DELETE /api/flocks/:id
```

### Growth Prediction

**Predict Growth with Image**
```http
POST /api/predictions/growth
Content-Type: multipart/form-data

flockId: "abc123..."
actualWeight: 450
feedType: "Starter Feed"
weekNumber: 5
feedImage: [file]
```

**Get Latest Prediction**
```http
GET /api/predictions/growth/:flockId/latest
```

### Feed Plan Generation

**Generate Feed Plan**
```http
POST /api/feed-plans/generate
Content-Type: application/json

{
  "flockId": "abc123...",
  "currentWeight": 450
}
```

**Get All Feed Plans**
```http
GET /api/feed-plans/:flockId
```

**Get Latest Feed Plan**
```http
GET /api/feed-plans/:flockId/latest
```

## 🧪 Testing API with Postman/Insomnia

1. **Create a Flock** (POST /api/flocks)
2. **Predict Growth** (POST /api/predictions/growth) - Upload feed plate image
3. **Generate Feed Plan** (POST /api/feed-plans/generate)
4. **View History** (GET /api/flocks/:id/history)

## 🤖 ML Models

### Weight Prediction Model
- **Model**: Linear Regression with polynomial features
- **Accuracy**: R² = 0.7703 (77%)
- **Input**: Age in days
- **Output**: Predicted weight in grams

### Feed Consumption Classification (ResNet50)
- **Model**: ResNet50 (transfer learning)
- **Classes**: 0%, 25%, 50%, 100%
- **Input**: RGB image (224x224)
- **Output**: Feed consumption percentage

## 📁 Project Structure

```
Integrated-Farm-System-Backend/
├── server.js              # Main Express server
├── package.json           # Node.js dependencies
├── .env                   # Environment variables
├── models/
│   ├── Flock.js          # Flock schema
│   ├── GrowthRecord.js   # Growth prediction records
│   └── FeedPlan.js       # Feed plan schema
├── routes/
│   ├── flockRoutes.js    # Flock CRUD operations
│   ├── predictionRoutes.js # Growth predictions & image classification
│   └── feedPlanRoutes.js # Feed plan generation
├── ml_service/
│   ├── app.py            # Flask ML service
│   └── requirements.txt  # Python dependencies
└── uploads/              # Uploaded feed images
```

## 🔧 Troubleshooting

**ML Service Error: Models not found**
- Ensure `data_anaysis/models/` directory exists with trained models
- Check paths in `ml_service/app.py`

**MongoDB Connection Error**
- Verify MongoDB is running: `mongod --version`
- Check connection string in `.env`

**Image Upload Error**
- Check `uploads/feed-images` directory permissions
- Verify image format (JPG, JPEG, PNG only)
- Max file size: 10MB

## 📊 Database Collections

### flocks
```javascript
{
  name: "Flock Alpha",
  breed: "Rhode Island Red",
  initialCount: 100,
  currentCount: 98,
  ageInWeeks: 4,
  createdAt: ISODate(),
  isActive: true
}
```

### growthrecords
```javascript
{
  flock: ObjectId,
  weekNumber: 5,
  ageInDays: 35,
  actualWeight: 450,
  predictedWeight: 430,
  feedConsumedPercentage: 75,
  feedType: "Starter Feed",
  imageUrl: "/uploads/feed-images/...",
  recommendation: "Weight is on target...",
  growthStatus: "On Target"
}
```

### feedplans
```javascript
{
  flock: ObjectId,
  weekNumber: 6,
  currentAge: 6,
  currentWeight: 500,
  growthStage: "Starter",
  nutritionPlan: { protein: 20, energy: 3000, calcium: 1.0, phosphorus: 0.7 },
  dailyFeedPerChicken: 30,
  weeklyFeedPerChicken: 210,
  totalWeeklyFeed: 20580,
  ingredients: { corn: 54, soybeanMeal: 34, wheat: 7, vitamins: 3, minerals: 2 },
  recommendations: [...]
}
```

## 🎓 Growth Stages & Feed Requirements

### Starter (0-6 weeks)
- Protein: 20%
- Energy: 3000 kcal/kg
- Corn: 54%, Soybean: 34%, Wheat: 7%

### Grower (7-18 weeks)
- Protein: 16%
- Energy: 2900 kcal/kg
- Corn: 60%, Soybean: 26%, Wheat: 9%

### Layer (19+ weeks)
- Protein: 18%
- Energy: 2850 kcal/kg
- Calcium: 3.5% (for eggshells)
- Corn: 58%, Soybean: 24%, Wheat: 8%

## 📝 Notes

- Always start ML service BEFORE backend API
- Image classification requires good lighting for accuracy
- Weight predictions work best for ages 1-300 days
- Feed calculations use 6% of body weight formula

## 👥 Team

Research Project - Final Year
Built with Node.js, Express, MongoDB, Python, Flask, TensorFlow
