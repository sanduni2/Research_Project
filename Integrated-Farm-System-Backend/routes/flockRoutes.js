const express = require('express');
const router = express.Router();
const Flock = require('../models/Flock');
const GrowthRecord = require('../models/GrowthRecord');

// CREATE new flock
router.post('/', async (req, res) => {
    try {
        const { name, breed, initialCount, ageInWeeks, notes } = req.body;

        // Validation
        if (!name || !breed || !initialCount || ageInWeeks === undefined) {
            return res.status(400).json({
                success: false,
                error: 'Please provide all required fields: name, breed, initialCount, ageInWeeks'
            });
        }

        // Create new flock
        const flock = new Flock({
            name,
            breed,
            initialCount,
            currentCount: initialCount,
            ageInWeeks,
            notes
        });

        await flock.save();

        res.status(201).json({
            success: true,
            message: 'Flock created successfully',
            data: flock
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// GET all flocks
router.get('/', async (req, res) => {
    try {
        const flocks = await Flock.find({ isActive: true })
            .sort({ createdAt: -1 })
            .select('name breed initialCount currentCount ageInWeeks notes createdAt updatedAt lastPredictionDate totalPredictions');

        res.json({
            success: true,
            count: flocks.length,
            data: flocks
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// GET single flock by ID
router.get('/:id', async (req, res) => {
    try {
        const flock = await Flock.findById(req.params.id);

        if (!flock) {
            return res.status(404).json({
                success: false,
                error: 'Flock not found'
            });
        }

        res.json({
            success: true,
            data: flock
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// GET flock history (all growth records)
router.get('/:id/history', async (req, res) => {
    try {
        const flock = await Flock.findById(req.params.id);

        if (!flock) {
            return res.status(404).json({
                success: false,
                error: 'Flock not found'
            });
        }

        const growthRecords = await GrowthRecord.find({ flock: req.params.id })
            .sort({ createdAt: -1 }) // Sort by newest first
            .select('-__v');

        res.json({
            success: true,
            flock: {
                name: flock.name,
                breed: flock.breed,
                currentAge: flock.ageInWeeks,
                currentCount: flock.currentCount,
                lastPredictionDate: flock.lastPredictionDate,
                totalPredictions: flock.totalPredictions || 0
            },
            recordCount: growthRecords.length,
            data: growthRecords
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// UPDATE flock
router.put('/:id', async (req, res) => {
    try {
        const flock = await Flock.findByIdAndUpdate(
            req.params.id,
            { ...req.body, updatedAt: Date.now() },
            { new: true, runValidators: true }
        );

        if (!flock) {
            return res.status(404).json({
                success: false,
                error: 'Flock not found'
            });
        }

        res.json({
            success: true,
            message: 'Flock updated successfully',
            data: flock
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// DELETE flock (soft delete)
router.delete('/:id', async (req, res) => {
    try {
        const flock = await Flock.findByIdAndUpdate(
            req.params.id,
            { isActive: false, updatedAt: Date.now() },
            { new: true }
        );

        if (!flock) {
            return res.status(404).json({
                success: false,
                error: 'Flock not found'
            });
        }

        res.json({
            success: true,
            message: 'Flock deleted successfully'
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

module.exports = router;
