# 🚀 SUPER EASY START GUIDE

## ⚡ **FASTEST WAY TO START** (Just 1 Click!)

### **Option 1: Double-Click Method** ⭐ EASIEST
1. Find the file **`start-all-services.bat`** in your Research folder
2. **Double-click it**
3. Wait 20 seconds
4. ✅ Done! All 3 services are running!

### **Option 2: PowerShell Method**
```powershell
cd C:\Users\Sanduni\Desktop\Research
.\start-all-services.ps1
```

---

## 📊 What You'll See

After running the script, you'll see:
```
============================================================
🚀 STARTING POULTRY FARM MANAGEMENT SYSTEM
============================================================

1️⃣  ML SERVICE (Python Flask)
   └─ Port: 5000
[ML-Service] ✅ Started

2️⃣  BACKEND API (Node.js + Express)
   └─ Port: 3000
[Backend-API] ✅ Started

3️⃣  FRONTEND (React Native + Expo)
   └─ Port: 8081
[Frontend-Expo] ✅ Started

============================================================
✅ ALL SERVICES STARTED!
============================================================
```

---

## 🛑 **TO STOP EVERYTHING** (Just 1 Click!)

### Method 1: Press Ctrl+C
- Just press **Ctrl+C** in the PowerShell window

### Method 2: Run Stop Script
- Double-click **`stop-all-services.bat`** (create this if needed)
- Or run: `.\stop-all-services.ps1`

---

## 📱 **TEST THE MOBILE APP**

### On Your Phone:
1. **Download** "Expo Go" app from Play Store/App Store
2. **Open** Expo Go
3. **Scan** the QR code that appears in the PowerShell window
4. **Wait** for app to load
5. ✅ **Start using** the app!

### On Computer (Android Emulator):
1. Look at the Expo window
2. Press **`a`** key
3. Android emulator will open automatically

---

## ✅ **VERIFY EVERYTHING WORKS**

### Quick Test Commands:
```powershell
# Test ML Service
Invoke-WebRequest http://localhost:5000/api/health

# Test Backend
Invoke-WebRequest http://localhost:3000/api/flocks

# Open Frontend in Browser
Start-Process http://localhost:8081
```

---

## 🎯 **ACCESS URLs**

| Service | URL | Purpose |
|---------|-----|---------|
| **ML Service** | http://localhost:5000 | AI Models |
| **Backend API** | http://localhost:3000 | Database & Logic |
| **Frontend Web** | http://localhost:8081 | Web Interface |
| **Mobile App** | Scan QR Code | Phone App |

---

## 🔥 **TROUBLESHOOTING**

### ❌ Script won't run?
```powershell
# Fix execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ Port already in use?
```powershell
# Run stop script first
.\stop-all-services.ps1
# Then start again
.\start-all-services.ps1
```

### ❌ Services not starting?
1. Check if MongoDB is running: `net start MongoDB`
2. Make sure Python venv exists: `C:\Users\Sanduni\Desktop\Research\.venv`
3. Make sure node_modules exist in Backend and Frontend folders

---

## 📁 **FILES YOU CREATED**

```
📁 C:\Users\Sanduni\Desktop\Research\
│
├── 🚀 start-all-services.bat       ← DOUBLE-CLICK THIS!
├── 🚀 start-all-services.ps1       ← PowerShell version
├── 🛑 stop-all-services.ps1        ← Stop everything
├── 📖 QUICK_START_GUIDE.md         ← Detailed guide
└── 📖 START_HERE.md                ← This file!
```

---

## 💡 **PRO TIPS**

1. **Keep the PowerShell window open** while using the app
2. **Don't close the window** or services will stop
3. **Check the logs** in PowerShell if something doesn't work
4. **Always stop services** before shutting down computer

---

## 🎉 **YOU'RE DONE!**

Your complete system is now running:
- ✅ AI Model (Weight Prediction - 77% accurate)
- ✅ Backend API (11 endpoints)
- ✅ Mobile App (3 screens)
- ✅ Database (MongoDB)

**Start creating flocks and testing predictions! 🐔**

---

## 🆘 **NEED HELP?**

1. Read the error message in PowerShell window
2. Try stopping and restarting: `.\stop-all-services.ps1` then `.\start-all-services.ps1`
3. Check MongoDB is running: `net start MongoDB`
4. Reinstall dependencies:
   ```powershell
   cd Integrated-Farm-System-Backend
   npm install
   
   cd ..\Integrated-Farm-System-Frontend
   npm install
   ```

---

**Last Updated**: January 5, 2026  
**Version**: 1.0.0
