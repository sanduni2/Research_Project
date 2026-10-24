const mongoose = require('mongoose');

const growthRecordSchema = new mongoose.Schema({
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
    ageInDays: {
        type: Number,
        required: [true, 'Age in days is required']
    },
    actualWeight: {
        type: Number,
        min: [0, 'Weight cannot be negative']
    },
    predictedWeight: {
        type: Number,
        required: [true, 'Predicted weight is required'],
        min: [0, 'Predicted weight cannot be negative']
    },
    weightDifference: {
        type: Number
    },
    feedConsumedPercentage: {
        type: Number,
        enum: [0, 25, 50, 100],
        required: [true, 'Feed consumed percentage is required']
    },
    feedType: {
        type: String,
        enum: ['Starter Feed', 'Grower Feed', 'Layer Feed', 'Mixed Feed'],
        required: [true, 'Feed type is required']
    },
    imageUrl: {
        type: String
    },
    recommendation: {
        type: String
    },
    growthStatus: {
        type: String,
        enum: ['Below Target', 'On Target', 'Above Target']
    },
    recordedAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true
});

// Calculate weight difference if actual weight is provided
growthRecordSchema.pre('save', function(next) {
    if (this.actualWeight && this.predictedWeight) {
        this.weightDifference = this.actualWeight - this.predictedWeight;
        
        // Determine growth status (within 10% is on target)
        const percentDifference = (this.weightDifference / this.predictedWeight) * 100;
        if (percentDifference < -10) {
            this.growthStatus = 'Below Target';
        } else if (percentDifference > 10) {
            this.growthStatus = 'Above Target';
        } else {
            this.growthStatus = 'On Target';
        }
    }
    next();
});

// Index for efficient querying
growthRecordSchema.index({ flock: 1, weekNumber: 1 });
growthRecordSchema.index({ flock: 1, recordedAt: -1 });

module.exports = mongoose.model('GrowthRecord', growthRecordSchema);
