# 🚀 QUICK START COMMANDS

## Start All Services
```powershell
.\start-services-simple.ps1
```

## Stop All Services
```powershell
.\stop-services-simple.ps1
```

---

## Manual Commands (if needed)

### Start MongoDB
```powershell
mongod --dbpath=C:\data\db --port=27017
```

### Start ML Service
```powershell
cd D:\Research\Integrated-Farm-System-Backend\ml_service
& D:\Research\.venv\Scripts\Activate.ps1
python app.py
```

### Start Backend
```powershell
cd D:\Research\Integrated-Farm-System-Backend
node server.js
```

### Start Frontend
```powershell
cd D:\Research\Integrated-Farm-System-Frontend
npm start
```

---

## Access URLs

- **Frontend Web**: http://localhost:8081
- **Backend API**: http://localhost:3000
- **ML Service Health**: http://localhost:5000/api/health
- **MongoDB**: localhost:27017

---

## Troubleshooting

### Check if services are running:
```powershell
Get-NetTCPConnection -LocalPort 3000,5000,8081,27017 -State Listen
```

### Force stop all:
```powershell
Get-Process node,python,mongod -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

## Current Status (as of your last run)
✅ All 4 services are running:
- MongoDB (27017)
- ML Service (5000)  
- Backend API (3000)
- Frontend (8081)

**Just open:** http://localhost:8081
