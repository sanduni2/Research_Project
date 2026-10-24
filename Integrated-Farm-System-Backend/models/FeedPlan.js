const mongoose = require('mongoose');

const feedPlanSchema = new mongoose.Schema({
    flock: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Flock',
        required: [true, 'Flock reference is required']
    },
    weekNumber: {
        type: Number,
        required: [true, 'Week number is required'],
        min: [0, 'Week number cannot be negative']
    },
    currentAge: {
        type: Number,
        required: [true, 'Current age is required']
    },
    currentWeight: {
        type: Number,
        required: [true, 'Current weight is required'],
        min: [0, 'Weight cannot be negative']
    },
    growthStage: {
        type: String,
        enum: ['Starter', 'Grower', 'Layer'],
        required: [true, 'Growth stage is required']
    },
    nutritionPlan: {
        protein: {
            type: Number,
            required: true,
            min: 0,
            max: 100
        },
        energy: {
            type: Number,
            required: true,
            min: 0
        },
        calcium: {
            type: Number,
            required: true,
            min: 0,
            max: 100
        },
        phosphorus: {
            type: Number,
            required: true,
            min: 0,
            max: 100
        }
    },
    dailyFeedPerChicken: {
        type: Number,
        required: [true, 'Daily feed per chicken is required'],
        min: [0, 'Daily feed cannot be negative']
    },
    weeklyFeedPerChicken: {
        type: Number,
        required: [true, 'Weekly feed per chicken is required'],
        min: [0, 'Weekly feed cannot be negative']
    },
    totalWeeklyFeed: {
        type: Number,
        required: [true, 'Total weekly feed is required'],
        min: [0, 'Total weekly feed cannot be negative']
    },
    ingredients: {
        corn: {
            type: Number,
            min: 0,
            max: 100
        },
        soybeanMeal: {
            type: Number,
            min: 0,
            max: 100
        },
        wheat: {
            type: Number,
            min: 0,
            max: 100
        },
        vitamins: {
            type: Number,
            min: 0,
            max: 100
        },
        minerals: {
            type: Number,
            min: 0,
            max: 100
        }
    },
    recommendations: [{
        type: String
    }],
    createdAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true
});

// Index for efficient querying
feedPlanSchema.index({ flock: 1, weekNumber: 1 });
feedPlanSchema.index({ flock: 1, createdAt: -1 });

module.exports = mongoose.model('FeedPlan', feedPlanSchema);
