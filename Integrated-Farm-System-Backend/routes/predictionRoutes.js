const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const Flock = require('../models/Flock');
const GrowthRecord = require('../models/GrowthRecord');

// Configure multer for image uploads
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadDir = 'uploads/feed-images';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, 'feed-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({
    storage: storage,
    limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
    fileFilter: function (req, file, cb) {
        console.log('🔍 Multer fileFilter received:', {
            originalname: file.originalname,
            mimetype: file.mimetype,
            fieldname: file.fieldname
        });
        
        const allowedTypes = /jpeg|jpg|png/;
        const allowedMimes = /image\/(jpeg|jpg|png)/;
        
        // Check file extension
        const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
        // Check MIME type (more flexible matching)
        const mimetype = allowedMimes.test(file.mimetype);
        
        console.log('🔍 Validation results:', { extname, mimetype });

        if (extname && mimetype) {
            console.log('✅ File validation passed');
            return cb(null, true);
        } else {
            console.log('❌ File validation failed');
            cb(new Error(`Only JPEG, JPG, and PNG images are allowed! Received: ${file.originalname} (${file.mimetype})`));
        }
    }
});

// ML Service URL
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:5000';

// TEST - Debug endpoint to check file upload
router.post('/test-upload', upload.single('feedImage'), (req, res) => {
    console.log('🔍 TEST UPLOAD ENDPOINT');
    console.log('   Body:', req.body);
    console.log('   File:', req.file);
    
    res.json({
        success: true,
        message: 'File upload test',
        hasFile: !!req.file,
        file: req.file ? {
            filename: req.file.filename,
            size: req.file.size,
            mimetype: req.file.mimetype,
            path: req.file.path
        } : null,
        body: req.body
    });
});

// POST - Generate initial feed plan for new flock (no image required)
router.post('/initial-feed-plan/:flockId', async (req, res) => {
    try {
        const { flockId } = req.params;

        // Get flock details
        const flock = await Flock.findById(flockId);
        if (!flock) {
            return res.status(404).json({
                success: false,
                error: 'Flock not found'
            });
        }

        // Calculate age in days
        const ageInDays = flock.ageInWeeks * 7;
        
        // Determine growth stage
        let growthStage;
        if (flock.ageInWeeks <= 6) {
            growthStage = 'Starter';
        } else if (flock.ageInWeeks <= 18) {
            growthStage = 'Grower';
        } else {
            growthStage = 'Layer';
        }

        // Determine recommended feed type based on stage
        let recommendedFeedType;
        let nutritionDetails;
        let feedIngredients;
        
        if (growthStage === 'Starter') {
            recommendedFeedType = 'Starter Feed (High Protein 20-24%)';
            nutritionDetails = {
                crudeProtein: 21,
                metabolizableEnergy: 2900, // kcal/kg
                calcium: 0.95,
                phosphorus: 0.42,
                lysine: 1.10,
                methionine: 0.48,
                fiber: 4.0,
                fat: 3.2
            };
            feedIngredients = [
                { name: 'Corn', percentage: 52 },
                { name: 'Soybean Meal', percentage: 32 },
                { name: 'Fish Meal', percentage: 6 },
                { name: 'Wheat', percentage: 6 },
                { name: 'Vitamins & Minerals', percentage: 4 }
            ];
        } else if (growthStage === 'Grower') {
            recommendedFeedType = 'Grower Feed (Medium Protein 16-18%)';
            nutritionDetails = {
                crudeProtein: 16,
                metabolizableEnergy: 2850,
                calcium: 0.85,
                phosphorus: 0.38,
                lysine: 0.80,
                methionine: 0.35,
                fiber: 4.5,
                fat: 2.8
            };
            feedIngredients = [
                { name: 'Corn', percentage: 62 },
                { name: 'Soybean Meal', percentage: 20 },
                { name: 'Wheat', percentage: 12 },
                { name: 'Rice Bran', percentage: 3 },
                { name: 'Vitamins & Minerals', percentage: 3 }
            ];
        } else {
            recommendedFeedType = 'Layer Feed (Calcium-enriched 16-18%)';
            nutritionDetails = {
                crudeProtein: 16,
                metabolizableEnergy: 2700,
                calcium: 3.5,
                phosphorus: 0.38,
                lysine: 0.72,
                methionine: 0.34,
                fiber: 5.0,
                fat: 2.5
            };
            feedIngredients = [
                { name: 'Corn', percentage: 55 },
                { name: 'Soybean Meal', percentage: 18 },
                { name: 'Limestone', percentage: 10 },
                { name: 'Wheat Bran', percentage: 10 },
                { name: 'Vitamins & Minerals', percentage: 7 }
            ];
        }

        // Predict weight from age using ML service
        let predictedWeight;
        try {
            const weightResponse = await axios.post(`${ML_SERVICE_URL}/api/predict/weight`, {
                age: ageInDays
            });
            
            predictedWeight = Math.round(weightResponse.data.predicted_weight || 0);
            
            if (!predictedWeight || predictedWeight === 0) {
                // Fallback calculation
                predictedWeight = Math.round(ageInDays * 10); // Rough estimate: 10g per day
            }
        } catch (error) {
            console.error('ML Service Error (Weight):', error.message);
            // Fallback calculation
            predictedWeight = Math.round(ageInDays * 10);
        }

        // Generate comprehensive recommendation
        let recommendation = `Welcome to your ${flock.breed} flock management!\n\n`;
        recommendation += `🐔 Current Stage: ${growthStage}\n`;
        recommendation += `📅 Age: ${flock.ageInWeeks} weeks (${ageInDays} days)\n`;
        recommendation += `⚖️ Expected Weight: ${predictedWeight}g per bird\n\n`;
        
        if (growthStage === 'Starter') {
            recommendation += `📋 Starter Stage Guidelines:\n`;
            recommendation += `• Feed: High protein (20-24%) starter feed\n`;
            recommendation += `• Quantity: ~50-75g per bird per day\n`;
            recommendation += `• Water: Fresh water always available\n`;
            recommendation += `• Monitor: Weight gain should be ~10g/day\n`;
            recommendation += `• Temperature: Keep brooder at 32-35°C\n\n`;
        } else if (growthStage === 'Grower') {
            recommendation += `📋 Grower Stage Guidelines:\n`;
            recommendation += `• Feed: Medium protein (16-18%) grower feed\n`;
            recommendation += `• Quantity: ~75-120g per bird per day\n`;
            recommendation += `• Water: Fresh water always available\n`;
            recommendation += `• Monitor: Steady weight gain expected\n`;
            recommendation += `• Space: Ensure adequate space (0.5-1 sq ft per bird)\n\n`;
        } else {
            recommendation += `📋 Layer Stage Guidelines:\n`;
            recommendation += `• Feed: Layer feed with calcium (16-18% protein)\n`;
            recommendation += `• Quantity: ~120-150g per bird per day\n`;
            recommendation += `• Water: Fresh water always available\n`;
            recommendation += `• Calcium: Ensure adequate for egg shells\n`;
            recommendation += `• Nesting: Provide clean nesting boxes\n\n`;
        }
        
        recommendation += `📱 Next Steps:\n`;
        recommendation += `1. Start monitoring daily feed consumption\n`;
        recommendation += `2. Upload feed plate images daily for 7 days\n`;
        recommendation += `3. Track bird health and behavior\n`;
        recommendation += `4. After 7 days, analyze performance and adjust plan if needed`;

        // Create initial feed plan record
        const initialFeedPlan = {
            weekNumber: Math.floor(flock.ageInWeeks),
            startDate: new Date(),
            feedType: recommendedFeedType,
            predictedWeight: predictedWeight,
            recommendation: recommendation,
            nutritionDetails: nutritionDetails,
            feedIngredients: feedIngredients,
            isActive: true
        };

        // Save feed plan to flock
        if (!flock.feedPlans) {
            flock.feedPlans = [];
        }
        flock.feedPlans.push(initialFeedPlan);
        flock.markModified('feedPlans');
        await flock.save();

        res.status(200).json({
            success: true,
            message: 'Initial feed plan generated successfully',
            data: {
                flockId: flock._id,
                flockName: flock.name,
                breed: flock.breed,
                ageInWeeks: flock.ageInWeeks,
                growthStage: growthStage,
                predictedWeight: predictedWeight,
                recommendedFeedType: recommendedFeedType,
                recommendation: recommendation,
                nutritionDetails: nutritionDetails,
                feedIngredients: feedIngredients,
                feedPlanId: initialFeedPlan._id
            }
        });

    } catch (error) {
        console.error('Initial Feed Plan Error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// POST - Predict growth with optional image
router.post('/growth', upload.single('feedImage'), async (req, res) => {
    try {
        const { flockId, actualWeight, feedType, weekNumber } = req.body;

        // Validation
        if (!flockId || !feedType) {
            return res.status(400).json({
                success: false,
                error: 'Please provide flockId and feedType'
            });
        }

        // Get flock details
        const flock = await Flock.findById(flockId);
        if (!flock) {
            return res.status(404).json({
                success: false,
                error: 'Flock not found'
            });
        }

        // Calculate age in days explicitly
        const ageInDays = flock.ageInWeeks * 7;
        const currentWeek = weekNumber || Math.floor(flock.ageInWeeks);

        console.log('Flock Age in Weeks:', flock.ageInWeeks);
        console.log('Calculated Age in Days:', ageInDays);

        // 1. Predict weight from age using ML service
        let predictedWeight;
        try {
            const weightResponse = await axios.post(`${ML_SERVICE_URL}/api/predict/weight`, {
                age: ageInDays
            });
            
            console.log('ML Service Response:', weightResponse.data);
            
            // ML service returns predicted_weight with underscore
            predictedWeight = Math.round(weightResponse.data.predicted_weight || 0);
            console.log('Predicted Weight after rounding:', predictedWeight);
            
            if (!predictedWeight || predictedWeight === 0) {
                console.warn('⚠️ Warning: ML service returned 0 or invalid weight');
                // Fallback calculation if ML service fails
                predictedWeight = Math.round(ageInDays * 10); // Rough estimate: 10g per day
            }
        } catch (error) {
            console.error('ML Service Error (Weight):', error.message);
            console.error('Error details:', error.response?.data || error);
            return res.status(503).json({
                success: false,
                error: 'ML Service is not available. Please ensure the ML service is running.'
            });
        }

        // 2. Classify feed image if provided
        let feedPercentage = null;
        let feedConfidence = null; // Store model confidence
        let imageUrl = null;

        console.log('📷 Image Upload Check:');
        console.log('   - req.file exists:', !!req.file);
        if (req.file) {
            console.log('   - File path:', req.file.path);
            console.log('   - File size:', req.file.size);
            console.log('   - File mimetype:', req.file.mimetype);
        }

        if (req.file) {
            try {
                console.log('🔄 Sending image to ML Service...');
                const formData = new FormData();
                formData.append('image', fs.createReadStream(req.file.path));

                const imageResponse = await axios.post(
                    `${ML_SERVICE_URL}/api/predict/feed-consumption`,
                    formData,
                    {
                        headers: formData.getHeaders(),
                        timeout: 30000 // 30 second timeout
                    }
                );

                console.log('✅ ML Service Response:', imageResponse.data);
                
                // IMPORTANT: Model predicts "remaining feed in plate" (0% = empty, 100% = full)
                // But we want to show "feed consumption" (0% = not eaten, 100% = all eaten)
                // So we need to INVERSE the prediction
                const plateFeedPercentage = imageResponse.data.predicted_percentage;
                const confidence = imageResponse.data.confidence;
                
                // Inverse calculation: if plate is 25% full, then 75% was consumed
                const rawFeedConsumed = 100 - plateFeedPercentage;
                
                // Map to nearest allowed enum value [0, 25, 50, 100]
                if (rawFeedConsumed <= 12.5) {
                    feedPercentage = 0;
                } else if (rawFeedConsumed <= 37.5) {
                    feedPercentage = 25;
                } else if (rawFeedConsumed <= 75) {
                    feedPercentage = 50;
                } else {
                    feedPercentage = 100;
                }
                
                feedConfidence = confidence; // Store for response
                
                imageUrl = `/uploads/feed-images/${req.file.filename}`;
                console.log(`📊 Plate Feed Remaining: ${plateFeedPercentage}%`);
                console.log(`📊 Feed Consumption Raw: ${rawFeedConsumed}%`);
                console.log(`📊 Feed Consumption (Mapped): ${feedPercentage}%`);
                console.log(`🎯 Model Confidence: ${confidence.toFixed(1)}%`);
                
                // Warn if confidence is low (less than 60%)
                if (confidence < 60) {
                    console.log(`⚠️  LOW CONFIDENCE WARNING - Result may be unreliable`);
                }

            } catch (error) {
                console.error('❌ ML Service Error (Image):');
                console.error('   - Message:', error.message);
                console.error('   - Response:', error.response?.data);
                console.error('   - Status:', error.response?.status);
                // Continue without image classification
                feedPercentage = 50; // Default fallback
                console.log('⚠️  Using fallback: 50%');
            }
        } else {
            console.log('⚠️  No image provided, using default: 50%');
            feedPercentage = 50; // Default if no image provided
        }

        // 3. Generate recommendation
        let recommendation = '';
        let growthStatus = '';

        if (actualWeight) {
            const weightDiff = actualWeight - predictedWeight;
            const percentDiff = (weightDiff / predictedWeight) * 100;

            if (percentDiff < -10) {
                growthStatus = 'Below Target';
                recommendation = `⚠️ Weight is ${Math.abs(percentDiff).toFixed(1)}% below target. ` +
                    `Increase protein intake and ensure adequate feeding. ` +
                    `Consider checking for health issues.`;
            } else if (percentDiff > 10) {
                growthStatus = 'Above Target';
                recommendation = `✅ Excellent! Weight is ${percentDiff.toFixed(1)}% above target. ` +
                    `Maintain current feeding schedule.`;
            } else {
                growthStatus = 'On Target';
                recommendation = `✅ Weight is on target. Continue current feeding practices.`;
            }

            // Add feed consumption advice
            if (feedPercentage === 0) {
                recommendation += ` 🚨 Feed plate is empty! Refill immediately.`;
            } else if (feedPercentage === 25) {
                recommendation += ` ⚠️ Feed is running low (25%). Consider refilling soon.`;
            } else if (feedPercentage === 50) {
                recommendation += ` ✓ Feed level is adequate (50%).`;
            } else {
                recommendation += ` ✓ Feed plate is full (100%).`;
            }
        } else {
            recommendation = `Predicted weight at ${ageInDays} days is ${predictedWeight}g. ` +
                `Provide ${feedType} and monitor growth weekly.`;
        }

        // 4. Save growth record
        const growthRecordData = {
            flock: flockId,
            weekNumber: currentWeek,
            ageInDays: ageInDays,
            actualWeight: actualWeight || null,
            predictedWeight: predictedWeight,
            feedConsumedPercentage: feedPercentage,
            feedType: feedType,
            imageUrl: imageUrl,
            recommendation: recommendation
        };

        // Only include growthStatus if actualWeight is provided
        if (actualWeight && growthStatus) {
            growthRecordData.growthStatus = growthStatus;
        }

        const growthRecord = new GrowthRecord(growthRecordData);
        await growthRecord.save();

        // Update flock's last prediction date and total predictions
        await Flock.findByIdAndUpdate(flockId, {
            lastPredictionDate: new Date(),
            $inc: { totalPredictions: 1 }
        });

        // 5. Return response
        res.status(201).json({
            success: true,
            message: 'Growth prediction completed',
            data: {
                flock: {
                    id: flock._id,
                    name: flock.name,
                    breed: flock.breed,
                    ageInWeeks: flock.ageInWeeks,
                    ageInDays: ageInDays
                },
                prediction: {
                    predictedWeight: predictedWeight,
                    actualWeight: actualWeight || null,
                    weightDifference: actualWeight ? (actualWeight - predictedWeight) : null,
                    growthStatus: actualWeight ? growthStatus : null
                },
                feedAnalysis: {
                    feedConsumedPercentage: feedPercentage,
                    feedConfidence: feedConfidence, // Add confidence score
                    feedType: feedType,
                    imageUrl: imageUrl
                },
                recommendation: recommendation,
                recordId: growthRecord._id
            }
        });

    } catch (error) {
        console.error('Prediction Error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// GET - Get latest prediction for a flock
router.get('/growth/:flockId/latest', async (req, res) => {
    try {
        const growthRecord = await GrowthRecord.findOne({ flock: req.params.flockId })
            .sort({ recordedAt: -1 })
            .populate('flock', 'name breed ageInWeeks');

        if (!growthRecord) {
            return res.status(404).json({
                success: false,
                error: 'No growth records found for this flock'
            });
        }

        res.json({
            success: true,
            data: growthRecord
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// GET - Get current week's feed tracking for a flock
router.get('/weekly-feed/:flockId', async (req, res) => {
    try {
        const flock = await Flock.findById(req.params.flockId);

        if (!flock) {
            return res.status(404).json({
                success: false,
                error: 'Flock not found'
            });
        }

        // Get the current incomplete week or the last completed week
        const currentWeek = flock.weeklyFeedTracking
            .slice()
            .reverse()
            .find(week => !week.isComplete) || 
            flock.weeklyFeedTracking[flock.weeklyFeedTracking.length - 1];

        res.json({
            success: true,
            data: {
                flockId: flock._id,
                flockName: flock.name,
                currentWeekNumber: flock.ageInWeeks,
                weeklyTracking: currentWeek || null,
                allWeeks: flock.weeklyFeedTracking
            }
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// POST - Upload feed image directly for weekly tracking
router.post('/upload-feed-image/:flockId', upload.single('feedImage'), async (req, res) => {
    try {
        const { flockId } = req.params;

        if (!req.file) {
            return res.status(400).json({
                success: false,
                error: 'Feed image is required'
            });
        }

        // Get flock details
        const flock = await Flock.findById(flockId);
        if (!flock) {
            return res.status(404).json({
                success: false,
                error: 'Flock not found'
            });
        }

        const currentWeek = Math.floor(flock.ageInWeeks);

        // Classify feed image using ML service
        let feedPercentage = 50; // Default
        let feedConfidence = 0;
        let imageUrl = `/uploads/feed-images/${req.file.filename}`;

        try {
            console.log('🔄 Sending image to ML Service for classification...');
            const formData = new FormData();
            formData.append('image', fs.createReadStream(req.file.path));

            const imageResponse = await axios.post(
                `${ML_SERVICE_URL}/api/predict/feed-consumption`,
                formData,
                {
                    headers: formData.getHeaders(),
                    timeout: 30000
                }
            );

            console.log('✅ ML Service Response:', imageResponse.data);
            
            const plateFeedPercentage = imageResponse.data.predicted_percentage;
            const confidence = imageResponse.data.confidence;
            
            // Inverse and map to valid enum values
            const rawFeedConsumed = 100 - plateFeedPercentage;
            
            if (rawFeedConsumed <= 12.5) {
                feedPercentage = 0;
            } else if (rawFeedConsumed <= 37.5) {
                feedPercentage = 25;
            } else if (rawFeedConsumed <= 75) {
                feedPercentage = 50;
            } else {
                feedPercentage = 100;
            }
            
            feedConfidence = confidence;
            
            console.log(`📊 Feed Consumption: ${feedPercentage}%`);
            console.log(`🎯 Confidence: ${confidence.toFixed(1)}%`);

        } catch (error) {
            console.error('❌ ML Service Error:', error.message);
            feedPercentage = 50; // Fallback
        }

        // Find or create current week's tracking
        let currentWeekTracking = flock.weeklyFeedTracking.find(
            week => week.weekNumber === currentWeek && !week.isComplete
        );

        if (!currentWeekTracking) {
            currentWeekTracking = {
                weekNumber: currentWeek,
                startDate: new Date(),
                dailyRecords: [],
                isComplete: false
            };
            flock.weeklyFeedTracking.push(currentWeekTracking);
        }

        const dayNumber = currentWeekTracking.dailyRecords.length + 1;

        if (dayNumber > 7) {
            return res.status(400).json({
                success: false,
                error: 'Week is already complete with 7 days'
            });
        }

        // Determine status (good/bad) based on percentage
        let status = 'good';
        let statusMessage = '';
        
        if (feedPercentage >= 75) {
            status = 'good';
            statusMessage = '✅ Excellent consumption';
        } else if (feedPercentage >= 50) {
            status = 'good';
            statusMessage = '✓ Good consumption';
        } else if (feedPercentage >= 25) {
            status = 'bad';
            statusMessage = '⚠️ Low consumption';
        } else {
            status = 'bad';
            statusMessage = '🚨 Critical - Very low';
        }

        // Add daily record
        currentWeekTracking.dailyRecords.push({
            dayNumber: dayNumber,
            date: new Date(),
            imageUrl: imageUrl,
            feedConsumedPercentage: feedPercentage,
            status: status
        });

        // Check if week is complete (7 days)
        if (dayNumber === 7) {
            currentWeekTracking.isComplete = true;
            
            // Calculate overall analysis
            const totalConsumption = currentWeekTracking.dailyRecords.reduce(
                (sum, day) => sum + day.feedConsumedPercentage, 0
            );
            const averageConsumption = Math.round(totalConsumption / 7);

            let overallStatus, overallMessage;
            if (averageConsumption >= 75) {
                overallStatus = 'Good';
                overallMessage = '✅ Excellent! Birds are eating well throughout the week.';
            } else if (averageConsumption >= 50) {
                overallStatus = 'Good';
                overallMessage = '✓ Good appetite. Feed consumption is adequate.';
            } else if (averageConsumption >= 25) {
                overallStatus = 'Needs Attention';
                overallMessage = '⚠️ Low feed consumption. Monitor bird health closely.';
            } else {
                overallStatus = 'Critical';
                overallMessage = '🚨 Critical! Very low feed intake. Check for health issues immediately.';
            }

            currentWeekTracking.overallAnalysis = {
                averageConsumption: averageConsumption,
                status: overallStatus,
                message: overallMessage
            };
        }

        // Mark the array as modified for Mongoose to detect changes
        flock.markModified('weeklyFeedTracking');
        await flock.save();

        res.status(201).json({
            success: true,
            message: 'Feed image uploaded and analyzed successfully',
            data: {
                dayNumber: dayNumber,
                date: new Date(),
                imageUrl: imageUrl,
                feedConsumedPercentage: feedPercentage,
                confidence: feedConfidence,
                status: status,
                statusMessage: statusMessage,
                weeklyTracking: {
                    weekNumber: currentWeekTracking.weekNumber,
                    totalDays: currentWeekTracking.dailyRecords.length,
                    isComplete: currentWeekTracking.isComplete,
                    overallAnalysis: currentWeekTracking.overallAnalysis
                }
            }
        });

    } catch (error) {
        console.error('Upload Feed Image Error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// NEW: Daily Analysis - Upload image and get comprehensive analysis
router.post('/daily-analysis/:flockId', upload.single('feedImage'), async (req, res) => {
    try {
        const { flockId } = req.params;
        const { actualWeight, feedType } = req.body;

        console.log('📊 Daily Analysis Request:', {
            flockId,
            actualWeight,
            feedType,
            hasFile: !!req.file
        });

        // Validate flock exists
        const flock = await Flock.findById(flockId);
        if (!flock) {
            return res.status(404).json({
                success: false,
                error: 'Flock not found'
            });
        }

        if (!req.file) {
            return res.status(400).json({
                success: false,
                error: 'Feed image is required'
            });
        }

        // Determine day number
        const dayNumber = (flock.dailyAnalysisRecords?.length || 0) + 1;
        
        if (dayNumber > 7) {
            return res.status(400).json({
                success: false,
                error: 'Already completed 7 days of analysis'
            });
        }

        // Call ML Service for feed consumption prediction
        const formData = new FormData();
        formData.append('image', fs.createReadStream(req.file.path));

        const mlResponse = await axios.post(
            `${ML_SERVICE_URL}/api/predict/feed-consumption`,
            formData,
            {
                headers: formData.getHeaders(),
                timeout: 60000
            }
        );

        const predictedPlateRemaining = mlResponse.data.predicted_percentage;
        const confidence = mlResponse.data.confidence;

        // Convert to feed consumed
        let rawFeedConsumed = 100 - predictedPlateRemaining;
        let currentDayFeedConsumption;
        
        if (rawFeedConsumed <= 12.5) {
            currentDayFeedConsumption = 0;
        } else if (rawFeedConsumed <= 37.5) {
            currentDayFeedConsumption = 25;
        } else if (rawFeedConsumed <= 75) {
            currentDayFeedConsumption = 50;
        } else {
            currentDayFeedConsumption = 100;
        }

        // Determine current day status
        const currentDayStatus = currentDayFeedConsumption >= 50 ? 'Good' : 'Bad';

        // Predict next day (simple heuristic - can be improved with ML)
        let nextDayFeedPrediction = currentDayFeedConsumption;
        if (currentDayFeedConsumption === 100) {
            nextDayFeedPrediction = 100;
        } else if (currentDayFeedConsumption >= 50) {
            nextDayFeedPrediction = Math.min(100, currentDayFeedConsumption + 25);
        }
        const nextDayStatus = nextDayFeedPrediction >= 50 ? 'Good' : 'Bad';

        // Predict weight based on flock age (using chickweight dataset patterns)
        // Average weight by week: Week0=40g, Week1=50g, Week2=90g, Week3=130g, Week4=180g, 
        // Week5=240g, Week6=300g, Week7=360g, Week8=420g, Week9=480g, Week10=540g, Week11=600g, Week12=650g
        const weeklyWeights = [40, 50, 90, 130, 180, 240, 300, 360, 420, 480, 540, 600, 650, 700, 750, 800, 850, 900];
        const ageInWeeks = Math.floor(flock.ageInWeeks);
        const predictedWeight = weeklyWeights[Math.min(ageInWeeks, weeklyWeights.length - 1)] || 900;

        // Construct image URL
        const imageUrl = `/uploads/feed-images/${req.file.filename}`;

        // Create daily analysis record
        const dailyRecord = {
            dayNumber,
            date: new Date(),
            imageUrl,
            currentDayFeedConsumption,
            currentDayStatus,
            nextDayFeedPrediction,
            nextDayStatus,
            predictedWeight,
            actualWeight: actualWeight ? parseFloat(actualWeight) : undefined,
            feedType: feedType || undefined,
            confidence
        };

        // Add to flock records
        if (!flock.dailyAnalysisRecords) {
            flock.dailyAnalysisRecords = [];
        }
        flock.dailyAnalysisRecords.push(dailyRecord);
        flock.updatedAt = new Date();

        await flock.save();

        console.log('✅ Daily analysis saved:', {
            dayNumber,
            currentDayFeedConsumption,
            currentDayStatus,
            predictedWeight
        });

        res.json({
            success: true,
            message: `Day ${dayNumber} analysis completed`,
            data: {
                dayNumber,
                imageUrl,
                currentDay: {
                    feedConsumption: currentDayFeedConsumption,
                    status: currentDayStatus
                },
                nextDay: {
                    feedPrediction: nextDayFeedPrediction,
                    status: nextDayStatus
                },
                weightPrediction: {
                    predicted: predictedWeight,
                    actual: actualWeight ? parseFloat(actualWeight) : null,
                    unit: 'grams'
                },
                feedType: feedType || null,
                confidence,
                totalDaysCompleted: flock.dailyAnalysisRecords.length,
                canGenerateFeedPlan: flock.dailyAnalysisRecords.length >= 7
            }
        });

    } catch (error) {
        console.error('Daily Analysis Error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get daily analysis records for a flock
router.get('/daily-analysis/:flockId', async (req, res) => {
    try {
        const { flockId } = req.params;

        const flock = await Flock.findById(flockId);
        if (!flock) {
            return res.status(404).json({
                success: false,
                error: 'Flock not found'
            });
        }

        res.json({
            success: true,
            data: {
                flockDetails: {
                    name: flock.name,
                    breed: flock.breed,
                    ageInWeeks: flock.ageInWeeks,
                    currentCount: flock.currentCount || flock.initialCount
                },
                dailyAnalysisRecords: flock.dailyAnalysisRecords || [],
                totalDaysCompleted: flock.dailyAnalysisRecords?.length || 0,
                canGenerateFeedPlan: (flock.dailyAnalysisRecords?.length || 0) >= 7,
                feedPlanGenerated: flock.feedPlanGenerated || false
            }
        });

    } catch (error) {
        console.error('Get Daily Analysis Error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// POST - Generate feed plan for next week based on current week's analysis
router.post('/generate-next-week-plan/:flockId', async (req, res) => {
    try {
        const { flockId } = req.params;
        const { weekNumber, previousWeekAnalysis } = req.body;

        const flock = await Flock.findById(flockId);
        if (!flock) {
            return res.status(404).json({
                success: false,
                error: 'Flock not found'
            });
        }

        // Deactivate all previous feed plans
        if (flock.feedPlans && flock.feedPlans.length > 0) {
            flock.feedPlans.forEach(plan => {
                plan.isActive = false;
            });
        }

        // Calculate age in days for next week
        const nextWeekAge = (flock.ageInWeeks + 1) * 7;
        
        // Determine growth stage
        let growthStage;
        if ((flock.ageInWeeks + 1) <= 6) {
            growthStage = 'Starter';
        } else if ((flock.ageInWeeks + 1) <= 18) {
            growthStage = 'Grower';
        } else {
            growthStage = 'Layer';
        }

        // Adjust feed type based on performance
        let recommendedFeedType;
        let nutritionDetails;
        let feedIngredients;
        const avgConsumption = previousWeekAnalysis?.averageConsumption || 50;
        
        if (avgConsumption < 50) {
            // Low consumption - try more palatable options
            if (growthStage === 'Starter') {
                recommendedFeedType = 'Premium Starter Feed (High Palatability, 22% Protein)';
                nutritionDetails = {
                    crudeProtein: 22,
                    metabolizableEnergy: 2950, // kcal/kg
                    calcium: 1.0,
                    phosphorus: 0.45,
                    lysine: 1.20,
                    methionine: 0.50,
                    fiber: 3.5,
                    fat: 3.5
                };
                feedIngredients = [
                    { name: 'Corn', percentage: 55 },
                    { name: 'Soybean Meal', percentage: 30 },
                    { name: 'Fish Meal', percentage: 8 },
                    { name: 'Wheat Bran', percentage: 3 },
                    { name: 'Vitamins & Minerals', percentage: 4 }
                ];
            } else if (growthStage === 'Grower') {
                recommendedFeedType = 'Enhanced Grower Feed (Improved Taste, 17% Protein)';
                nutritionDetails = {
                    crudeProtein: 17,
                    metabolizableEnergy: 2900,
                    calcium: 0.9,
                    phosphorus: 0.40,
                    lysine: 0.85,
                    methionine: 0.38,
                    fiber: 4.0,
                    fat: 3.0
                };
                feedIngredients = [
                    { name: 'Corn', percentage: 60 },
                    { name: 'Soybean Meal', percentage: 22 },
                    { name: 'Wheat', percentage: 10 },
                    { name: 'Sunflower Meal', percentage: 4 },
                    { name: 'Vitamins & Minerals', percentage: 4 }
                ];
            } else {
                recommendedFeedType = 'Premium Layer Feed (Calcium-enriched, 17% Protein)';
                nutritionDetails = {
                    crudeProtein: 17,
                    metabolizableEnergy: 2750,
                    calcium: 3.8,
                    phosphorus: 0.40,
                    lysine: 0.75,
                    methionine: 0.36,
                    fiber: 4.5,
                    fat: 2.8
                };
                feedIngredients = [
                    { name: 'Corn', percentage: 58 },
                    { name: 'Soybean Meal', percentage: 20 },
                    { name: 'Limestone', percentage: 8 },
                    { name: 'Wheat Bran', percentage: 8 },
                    { name: 'Vitamins & Minerals', percentage: 6 }
                ];
            }
        } else {
            // Good consumption - continue standard
            if (growthStage === 'Starter') {
                recommendedFeedType = 'Starter Feed (High Protein 20-24%)';
                nutritionDetails = {
                    crudeProtein: 21,
                    metabolizableEnergy: 2900,
                    calcium: 0.95,
                    phosphorus: 0.42,
                    lysine: 1.10,
                    methionine: 0.48,
                    fiber: 4.0,
                    fat: 3.2
                };
                feedIngredients = [
                    { name: 'Corn', percentage: 52 },
                    { name: 'Soybean Meal', percentage: 32 },
                    { name: 'Fish Meal', percentage: 6 },
                    { name: 'Wheat', percentage: 6 },
                    { name: 'Vitamins & Minerals', percentage: 4 }
                ];
            } else if (growthStage === 'Grower') {
                recommendedFeedType = 'Grower Feed (Medium Protein 16-18%)';
                nutritionDetails = {
                    crudeProtein: 16,
                    metabolizableEnergy: 2850,
                    calcium: 0.85,
                    phosphorus: 0.38,
                    lysine: 0.80,
                    methionine: 0.35,
                    fiber: 4.5,
                    fat: 2.8
                };
                feedIngredients = [
                    { name: 'Corn', percentage: 62 },
                    { name: 'Soybean Meal', percentage: 20 },
                    { name: 'Wheat', percentage: 12 },
                    { name: 'Rice Bran', percentage: 3 },
                    { name: 'Vitamins & Minerals', percentage: 3 }
                ];
            } else {
                recommendedFeedType = 'Layer Feed (Calcium-enriched 16-18%)';
                nutritionDetails = {
                    crudeProtein: 16,
                    metabolizableEnergy: 2700,
                    calcium: 3.5,
                    phosphorus: 0.38,
                    lysine: 0.72,
                    methionine: 0.34,
                    fiber: 5.0,
                    fat: 2.5
                };
                feedIngredients = [
                    { name: 'Corn', percentage: 55 },
                    { name: 'Soybean Meal', percentage: 18 },
                    { name: 'Limestone', percentage: 10 },
                    { name: 'Wheat Bran', percentage: 10 },
                    { name: 'Vitamins & Minerals', percentage: 7 }
                ];
            }
        }

        // Predict weight
        let predictedWeight;
        try {
            const weightResponse = await axios.post(`${ML_SERVICE_URL}/api/predict/weight`, {
                age: nextWeekAge
            });
            predictedWeight = Math.round(weightResponse.data.predicted_weight || 0);
            if (!predictedWeight || predictedWeight === 0) {
                predictedWeight = Math.round(nextWeekAge * 10);
            }
        } catch (error) {
            console.error('ML Service  Error:', error.message);
            predictedWeight = Math.round(nextWeekAge * 10);
        }

        // Generate adjusted recommendation
        let recommendation = `📊 Week ${weekNumber} Feed Plan (Adjusted Based on Previous Performance)\n\n`;
        recommendation += `📈 Previous Week Analysis:\n`;
        recommendation += `• Average Consumption: ${avgConsumption}%\n`;
        recommendation += `• Status: ${previousWeekAnalysis?.status || 'N/A'}\n\n`;
        
        if (avgConsumption < 50) {
            recommendation += `⚠️ ADJUSTMENTS MADE:\n`;
            recommendation += `• Switched to more palatable feed formulation\n`;
            recommendation += `• Increased feeding frequency recommended\n`;
            recommendation += `• Check water availability and quality\n`;
            recommendation += `• Monitor for health issues\n`;
            recommendation += `• Ensure comfortable environment temperature\n\n`;
        } else {
            recommendation += `✅ GOOD PERFORMANCE:\n`;
            recommendation += `• Maintaining current successful feed type\n`;
            recommendation += `• Continue current feeding schedule\n`;
            recommendation += `• Keep monitoring daily consumption\n\n`;
        }
        
        recommendation += `🎯 This Week's Plan:\n`;
        recommendation += `• Stage: ${growthStage}\n`;
        recommendation += `• Feed Type: ${recommendedFeedType}\n`;
        recommendation += `• Expected Weight: ${predictedWeight}g per bird\n`;
        recommendation += `• Age: ${flock.ageInWeeks + 1} weeks\n\n`;
        
        recommendation += `📋 Daily Tasks:\n`;
        recommendation += `1. Upload feed plate image daily\n`;
        recommendation += `2. Monitor consumption status (Good/Bad)\n`;
        recommendation += `3. Watch for behavior changes\n`;
        recommendation += `4. Maintain cleanliness\n`;
        recommendation += `5. After 7 days, analyze again`;

        // Create new feed plan
        const newFeedPlan = {
            weekNumber: weekNumber,
            startDate: new Date(),
            feedType: recommendedFeedType,
            predictedWeight: predictedWeight,
            recommendation: recommendation,
            nutritionDetails: nutritionDetails,
            feedIngredients: feedIngredients,
            isActive: true,
            weeklyPerformance: {
                averageConsumption: avgConsumption,
                status: previousWeekAnalysis?.status || 'unknown',
                shouldGenerateNewPlan: avgConsumption < 50
            }
        };

        if (!flock.feedPlans) {
            flock.feedPlans = [];
        }
        flock.feedPlans.push(newFeedPlan);
        flock.markModified('feedPlans');
        
        await flock.save();

        res.status(200).json({
            success: true,
            message: 'New feed plan generated successfully for next week',
            data: {
                feedPlan: newFeedPlan,
                adjustmentsMade: avgConsumption < 50
            }
        });

    } catch (error) {
        console.error('Generate Next Week Plan Error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

module.exports = router;
