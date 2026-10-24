const mongoose = require('mongoose');

const flockSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, 'Flock name is required'],
        trim: true
    },
    breed: {
        type: String,
        required: [true, 'Breed is required'],
        enum: ['Rhode Island Red', 'Leghorn', 'Plymouth Rock', 'Sussex', 'Orpington', 'Wyandotte', 'Brahma', 'Cochin', 'Silkie', 'Other'],
        trim: true
    },
    initialCount: {
        type: Number,
        required: [true, 'Initial count is required'],
        min: [1, 'Initial count must be at least 1']
    },
    currentCount: {
        type: Number,
        min: [0, 'Current count cannot be negative']
    },
    ageInWeeks: {
        type: Number,
        required: [true, 'Age is required'],
        min: [0, 'Age cannot be negative']
    },
    createdAt: {
        type: Date,
        default: Date.now
    },
    updatedAt: {
        type: Date,
        default: Date.now
    },
    isActive: {
        type: Boolean,
        default: true
    },
    notes: {
        type: String,
        trim: true
    },
    lastPredictionDate: {
        type: Date
    },
    totalPredictions: {
        type: Number,
        default: 0
    },
    // Daily analysis records (new flow)
    dailyAnalysisRecords: [{
        dayNumber: {
            type: Number,
            required: true
        },
        date: {
            type: Date,
            required: true,
            default: Date.now
        },
        imageUrl: {
            type: String,
            required: true
        },
        // Current day analysis
        currentDayFeedConsumption: {
            type: Number,
            enum: [0, 25, 50, 100],
            required: true
        },
        currentDayStatus: {
            type: String,
            enum: ['Good', 'Bad'],
            required: true
        },
        // Next day prediction
        nextDayFeedPrediction: {
            type: Number,
            enum: [0, 25, 50, 100]
        },
        nextDayStatus: {
            type: String,
            enum: ['Good', 'Bad']
        },
        // Weight prediction based on age
        predictedWeight: {
            type: Number // in grams
        },
        actualWeight: {
            type: Number // in grams, optional
        },
        feedType: {
            type: String,
            trim: true
        },
        confidence: {
            type: Number // ML model confidence
        }
    }],
    // Feed plan generation status
    feedPlanGenerated: {
        type: Boolean,
        default: false
    },
    feedPlanData: {
        generatedAt: Date,
        recommendations: String,
        optimizationScore: Number
    },
    // Weekly feed tracking (for Weekly Feed Consumption Tracker component)
    weeklyFeedTracking: [{
        weekNumber: {
            type: Number,
            required: true
        },
        startDate: {
            type: Date,
            required: true,
            default: Date.now
        },
        dailyRecords: [{
            dayNumber: {
                type: Number,
                required: true,
                min: 1,
                max: 7
            },
            date: {
                type: Date,
                required: true,
                default: Date.now
            },
            imageUrl: {
                type: String,
                required: true
            },
            feedConsumedPercentage: {
                type: Number,
                enum: [0, 25, 50, 100],
                required: true
            },
            status: {
                type: String,
                enum: ['good', 'bad'],
                default: 'good'
            }
        }],
        isComplete: {
            type: Boolean,
            default: false
        },
        overallAnalysis: {
            averageConsumption: Number,
            status: String,
            message: String
        }
    }],
    // Feed plans by week
    feedPlans: [{
        weekNumber: {
            type: Number,
            required: true
        },
        startDate: {
            type: Date,
            required: true,
            default: Date.now
        },
        feedType: {
            type: String,
            required: true
        },
        predictedWeight: {
            type: Number
        },
        recommendation: {
            type: String
        },
        nutritionDetails: {
            crudeProtein: Number,          // %
            metabolizableEnergy: Number,   // kcal/kg
            calcium: Number,               // %
            phosphorus: Number,            // %
            lysine: Number,                // %
            methionine: Number,            // %
            fiber: Number,                 // %
            fat: Number                    // %
        },
        feedIngredients: [{
            name: String,
            percentage: Number
        }],
        isActive: {
            type: Boolean,
            default: false
        },
        weeklyPerformance: {
            averageConsumption: Number,
            status: String, // 'good', 'needs-improvement', 'critical'
            shouldGenerateNewPlan: Boolean
        }
    }]
}, {
    timestamps: true
});

// Calculate age in days
flockSchema.virtual('ageInDays').get(function() {
    return this.ageInWeeks * 7;
});

// Growth stage based on age
flockSchema.virtual('growthStage').get(function() {
    if (this.ageInWeeks <= 6) return 'Starter';
    if (this.ageInWeeks <= 18) return 'Grower';
    return 'Layer';
});

// Ensure virtuals are included in JSON output
flockSchema.set('toJSON', { virtuals: true });
flockSchema.set('toObject', { virtuals: true });

module.exports = mongoose.model('Flock', flockSchema);
