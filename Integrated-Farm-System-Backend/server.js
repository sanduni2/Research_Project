require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const multer = require('multer');
const path = require('path');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use('/uploads', express.static('uploads'));

// MongoDB Connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/poultry_farm';

mongoose.connect(MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true
})
.then(() => console.log('✅ MongoDB Connected'))
.catch(err => console.error('❌ MongoDB Connection Error:', err));

// Import Routes
const flockRoutes = require('./routes/flockRoutes');
const predictionRoutes = require('./routes/predictionRoutes');
const feedPlanRoutes = require('./routes/feedPlanRoutes');

// Use Routes
app.use('/api/flocks', flockRoutes);
app.use('/api/predictions', predictionRoutes);
app.use('/api/feed-plans', feedPlanRoutes);

// Health Check
app.get('/api/health', (req, res) => {
    res.json({
        success: true,
        message: 'Poultry Farm System API is running',
        timestamp: new Date().toISOString()
    });
});

// Error Handler
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        success: false,
        error: err.message || 'Internal Server Error'
    });
});

// Start Server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log(`🚀 Server running on http://localhost:${PORT}`);
    console.log('='.repeat(60));
});

module.exports = app;
