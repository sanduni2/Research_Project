# 🚀 Quick Start Guide - Integrated Farm System

## ⚡ 5-Minute Setup

### Prerequisites Check
- ✅ Node.js installed? (`node --version`)
- ✅ Python installed? (`python --version`)
- ✅ MongoDB installed? (`mongod --version`)

---

## 🎯 Step-by-Step Setup

### 1️⃣ Install Dependencies (One Time Only)

```powershell
# Backend
cd Integrated-Farm-System-Backend
npm install

# ML Service
cd ml_service
pip install -r requirements.txt
cd ..

# Frontend
cd ..\Integrated-Farm-System-Frontend
npm install
cd ..
```

### 2️⃣ Start Services (Every Time)

**Open 3 PowerShell terminals in the Research folder:**

#### Terminal 1: ML Service (Flask)
```powershell
cd Integrated-Farm-System-Backend\ml_service
python app.py
```
✅ Wait for: "🚀 Starting ML Service on http://localhost:5000"

#### Terminal 2: Backend API (Node.js)
```powershell
cd Integrated-Farm-System-Backend
npm start
```
✅ Wait for: "🚀 Server running on http://localhost:3000"

#### Terminal 3: Frontend (React Native)
```powershell
cd Integrated-Farm-System-Frontend
npm start
```
✅ Wait for: QR code and menu

### 3️⃣ Run Mobile App

**Option A: Android Emulator**
- Press `a` in the terminal

**Option B: Physical Device**
1. Install Expo Go app from Play Store/App Store
2. Scan QR code
3. Wait for app to load

---

## 📱 Using the App

### Step 1: Create Flock
1. Enter flock name (e.g., "My First Flock")
2. Select breed (e.g., "Rhode Island Red")
3. Enter count (e.g., 100)
4. Enter age in weeks (e.g., 4)
5. Click "Create Flock & Continue"

### Step 2: Predict Growth
1. View your flock details
2. Optionally enter actual weight (e.g., 450g)
3. Select feed type (e.g., "Starter Feed")
4. Click "Take Photo" or "Choose Image" to upload feed plate
5. Click "Analyze Growth"
6. View prediction results

### Step 3: Get Feed Plan
1. Automatically generated after prediction
2. View nutrition requirements
3. See feed quantities and composition
4. Read recommendations

---

## 🔍 Verify Everything is Working

### Check ML Service
```powershell
curl http://localhost:5000/api/health
```
Should return: `{"success": true, "message": "ML Service is running"}`

### Check Backend API
```powershell
curl http://localhost:3000/api/health
```
Should return: `{"success": true, "message": "Poultry Farm System API is running"}`

### Check MongoDB
```powershell
mongosh
show dbs
```
Should show list of databases

---

## ❌ Common Issues & Quick Fixes

### Issue: ML Service won't start
```
ModuleNotFoundError: No module named 'flask'
```
**Fix**:
```powershell
cd Integrated-Farm-System-Backend\ml_service
pip install -r requirements.txt
```

### Issue: Backend API error
```
Error: Cannot find module 'express'
```
**Fix**:
```powershell
cd Integrated-Farm-System-Backend
npm install
```

### Issue: MongoDB not running
```
MongoNetworkError: connect ECONNREFUSED
```
**Fix**:
```powershell
net start MongoDB
```

### Issue: Frontend can't connect to backend
```
Network Error
```
**Fix**:
1. Check if ML service is running (Terminal 1)
2. Check if backend is running (Terminal 2)
3. Update API URL in `src/config/apiConfig.js` if using physical device

### Issue: Expo won't start
```
Metro bundler failed
```
**Fix**:
```powershell
npm start -- --reset-cache
```

---

## 📂 Project Folders

```
Research/
├── data_anaysis/                 # ML models (already trained)
├── Integrated-Farm-System-Backend/    # Node.js + Flask
│   ├── ml_service/              # Python ML API (Run First!)
│   └── server.js                # Node.js API (Run Second!)
└── Integrated-Farm-System-Frontend/   # React Native App (Run Third!)
```

---

## 🎥 Execution Order (Important!)

**ALWAYS start in this order:**

1. **ML Service** (Port 5000) - Flask Python
2. **Backend API** (Port 3000) - Node.js Express
3. **Frontend App** (Port 19000+) - React Native Expo

If you start them in wrong order, you'll get connection errors!

---

## 💡 Tips

1. **Keep terminals open**: Don't close the 3 terminals while using the app
2. **MongoDB auto-start**: MongoDB might already be running as a Windows service
3. **Use Expo Go**: Easiest way to test on physical devices
4. **Save IP address**: If using physical device, save your computer's IP for next time
5. **Check logs**: Look at terminal outputs for error messages

---

## 🆘 Need Help?

1. Check all 3 terminals for error messages
2. Verify all services are running (green ✅)
3. Read the complete guide: [README_COMPLETE_GUIDE.md](README_COMPLETE_GUIDE.md)
4. Check API docs: [Integrated-Farm-System-Backend/README_API.md](Integrated-Farm-System-Backend/README_API.md)

---

## ✅ Success Checklist

- [ ] ML Service running on port 5000
- [ ] Backend API running on port 3000
- [ ] Frontend showing QR code
- [ ] MongoDB connected (check Backend terminal)
- [ ] App loaded on device/emulator
- [ ] Can create a flock
- [ ] Can predict growth
- [ ] Can generate feed plan

---

**All set? Let's start farming! 🐔🌾**
