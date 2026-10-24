# 🚀 Quick Start Guide - Poultry Farm Management System

## ⚡ Starting All Services (Easy Way)

### Option 1: Double-click the batch file
1. **Double-click** `start-all-services.bat`
2. Wait 15-20 seconds for all services to start
3. Done! ✅

### Option 2: Run PowerShell script
1. Open PowerShell in this folder
2. Run: `.\start-all-services.ps1`
3. Wait for services to start

---

## 🛑 Stopping All Services

### Option 1: Press Ctrl+C in the startup window
- Simply press `Ctrl+C` in the PowerShell window

### Option 2: Run stop script
1. Open PowerShell in this folder
2. Run: `.\stop-all-services.ps1`

---

## 📋 What Gets Started?

When you run the startup script, these 3 services start automatically:

### 1️⃣ ML Service (Python Flask)
- **Port**: 5000
- **URL**: http://localhost:5000/api/health
- **Purpose**: Serves machine learning models
  - Weight prediction model (77% accuracy)
  - Feed consumption image classification

### 2️⃣ Backend API (Node.js + Express)
- **Port**: 3000
- **URL**: http://localhost:3000/api/flocks
- **Purpose**: REST API server
  - Manages flock data
  - Handles predictions
  - Generates feed plans

### 3️⃣ Frontend (React Native + Expo)
- **Port**: 8081
- **URL**: http://localhost:8081
- **Mobile**: exp://192.168.8.148:8081
- **Purpose**: Mobile application interface

---

## 📱 Testing the Mobile App

1. **Install Expo Go** on your phone:
   - Android: Play Store → "Expo Go"
   - iOS: App Store → "Expo Go"

2. **Connect your phone**:
   - Open Expo Go app
   - Scan the QR code from the terminal
   - App will load on your phone

3. **Use Android Emulator** (alternative):
   - Press `a` in the Expo terminal window
   - Android emulator will open automatically

---

## 🧪 Testing the APIs

### Test ML Service
```powershell
# Test health endpoint
Invoke-WebRequest -Uri "http://localhost:5000/api/health" -Method GET

# Test weight prediction
$body = '{"age": 14}'
Invoke-WebRequest -Uri "http://localhost:5000/api/predict/weight" `
    -Method POST -Body $body -ContentType "application/json"
```

### Test Backend API
```powershell
# Get all flocks
Invoke-WebRequest -Uri "http://localhost:3000/api/flocks" -Method GET

# Create a flock
$body = @{
    breedType = "Broiler"
    flockName = "Test Flock"
    numberOfChickens = 100
    ageInWeeks = 2
    notes = "Test flock"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:3000/api/flocks" `
    -Method POST -Body $body -ContentType "application/json"
```

---

## 🔧 Troubleshooting

### Services won't start?
1. Check if ports are already in use:
   ```powershell
   Get-NetTCPConnection -LocalPort 3000,5000,8081
   ```
2. Run the stop script: `.\stop-all-services.ps1`
3. Try starting again

### Can't find Python/Node?
- Make sure you've run `install.bat` or `install.ps1` first
- Check that Python virtual environment is activated

### MongoDB connection error?
- Start MongoDB service:
  ```powershell
  net start MongoDB
  ```

### Frontend shows errors?
- Navigate to Frontend folder:
  ```powershell
  cd Integrated-Farm-System-Frontend
  npm install
  ```

---

## 📁 Project Structure

```
Research/
├── start-all-services.ps1          ← 🚀 START HERE
├── start-all-services.bat          ← Or double-click this
├── stop-all-services.ps1           ← Stop all services
├── QUICK_START_GUIDE.md           ← This file
│
├── Integrated-Farm-System-Backend/
│   ├── server.js                   ← Node.js API (Port 3000)
│   ├── ml_service/
│   │   └── app.py                  ← Flask ML Service (Port 5000)
│   └── models/                     ← Database models
│
├── Integrated-Farm-System-Frontend/
│   ├── App.js                      ← React Native app (Port 8081)
│   └── src/screens/                ← 3 main screens
│
└── data_anaysis/
    └── models/                     ← Trained ML models
```

---

## ✅ Verification Checklist

After starting services, verify everything works:

- [ ] ML Service responds: http://localhost:5000/api/health
- [ ] Backend API responds: http://localhost:3000/api/flocks
- [ ] Frontend loads: http://localhost:8081
- [ ] QR code appears in terminal for mobile testing
- [ ] No error messages in PowerShell window

---

## 🎯 Common Commands

```powershell
# Start everything
.\start-all-services.ps1

# Stop everything
.\stop-all-services.ps1

# Check service status
Get-Job

# View service logs
Get-Job | Receive-Job

# Kill specific port
Stop-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess -Force
```

---

## 📞 Need Help?

1. Check the logs in the PowerShell window
2. Review the error messages
3. Try stopping and restarting services
4. Check MongoDB is running
5. Verify all dependencies are installed

---

## 🎉 You're Ready!

Your complete Poultry Farm Management System is now running with:
- ✅ AI-powered weight prediction
- ✅ Image-based feed consumption detection
- ✅ REST API backend
- ✅ Mobile-friendly interface

**Happy farming! 🐔**
