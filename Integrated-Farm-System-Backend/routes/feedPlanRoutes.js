const express = require('express');
const router = express.Router();
const Flock = require('../models/Flock');
const FeedPlan = require('../models/FeedPlan');

// Helper function to generate feed plan based on age and weight
function generateFeedPlan(ageInWeeks, weight, chickenCount, breed = 'Standard', predictedWeight = null) {
    let growthStage, nutritionPlan, ingredients, recommendations;

    // Calculate weight-adjusted nutrition multiplier
    let expectedWeight = predictedWeight;
    if (!expectedWeight) {
        if (ageInWeeks <= 6) {
            expectedWeight = 100 + (ageInWeeks * 50);
        } else if (ageInWeeks <= 18) {
            expectedWeight = 400 + ((ageInWeeks - 6) * 100);
        } else {
            expectedWeight = 1800;
        }
    }

    // Adjust protein AND feed quantity based on actual vs expected weight
    const weightRatio = weight ? (weight / expectedWeight) : 1.0;
    const proteinAdjust = weightRatio < 0.85 ? 2 : (weightRatio > 1.15 ? -1 : 0);
    
    // Feed quantity adjustment multiplier
    let feedMultiplier = 1.0;
    if (weightRatio > 1.15) {
        // Overweight - reduce feed by 20%
        feedMultiplier = 0.80;
    } else if (weightRatio < 0.85) {
        // Underweight - increase feed by 15%
        feedMultiplier = 1.15;
    }

    // Determine growth stage and nutrition requirements
    if (ageInWeeks <= 6) {
        // Starter Stage (0-6 weeks)
        growthStage = 'Starter';
        nutritionPlan = {
            protein: 20 + proteinAdjust,
            energy: 3000,
            calcium: 1.0,
            phosphorus: 0.7
        };
        // Adjust ingredients based on protein needs
        const baseProtein = 20;
        const proteinChange = proteinAdjust;
        const soybeanAdjust = Math.round(proteinChange * 1.5); // Soybean has ~44% protein
        const cornAdjust = -soybeanAdjust; // Compensate with corn
        
        ingredients = {
            corn: 54 + cornAdjust,
            soybeanMeal: 34 + soybeanAdjust,
            wheat: 7,
            vitamins: 3,
            minerals: 2
        };
        recommendations = [
            'Provide starter feed with 20% protein',
            'Ensure constant access to clean water',
            'Keep feeding area clean and dry',
            'Monitor chick behavior and appetite daily',
            'Maintain proper brooding temperature (95°F week 1, reduce 5°F weekly)'
        ];

    } else if (ageInWeeks <= 18) {
        // Grower Stage (7-18 weeks)
        growthStage = 'Grower';
        nutritionPlan = {
            protein: 16 + proteinAdjust,
            energy: 2900,
            calcium: 0.9,
            phosphorus: 0.6
        };
        // Adjust ingredients based on protein needs
        const soybeanAdjust = Math.round(proteinAdjust * 1.5);
        const cornAdjust = -soybeanAdjust;
        
        ingredients = {
            corn: 60 + cornAdjust,
            soybeanMeal: 26 + soybeanAdjust,
            wheat: 9,
            vitamins: 3,
            minerals: 2
        };
        recommendations = [
            'Provide grower feed with 16% protein',
            'Gradually increase feeding space per bird',
            'Monitor weight gain weekly',
            'Ensure adequate ventilation',
            'Introduce perches for roosting'
        ];

    } else {
        // Layer Stage (19+ weeks)
        growthStage = 'Layer';
        nutritionPlan = {
            protein: 18 + proteinAdjust,
            energy: 2850,
            calcium: 3.5,
            phosphorus: 0.45
        };
        // Adjust ingredients based on protein needs
        const soybeanAdjust = Math.round(proteinAdjust * 1.5);
        const cornAdjust = -soybeanAdjust;
        
        ingredients = {
            corn: 58 + cornAdjust,
            soybeanMeal: 24 + soybeanAdjust,
            wheat: 8,
            vitamins: 5,
            minerals: 5
        };
        recommendations = [
            'Provide layer feed with 18% protein and 3.5% calcium',
            'Offer oyster shells separately for extra calcium',
            'Maintain 14-16 hours of light daily for optimal egg production',
            'Provide nesting boxes (1 per 4-5 hens)',
            'Collect eggs 2-3 times daily to prevent breakage'
        ];
    }

    // Calculate daily feed per chicken (formula: 6% of body weight)
    // If weight not provided, use age-based estimates
    let estimatedWeight = weight;
    if (!estimatedWeight) {
        if (ageInWeeks <= 6) {
            estimatedWeight = 100 + (ageInWeeks * 50); // Starter: ~100-400g
        } else if (ageInWeeks <= 18) {
            estimatedWeight = 400 + ((ageInWeeks - 6) * 100); // Grower: ~400-1600g
        } else {
            estimatedWeight = 1800; // Layer: ~1800-2000g
        }
    }

    // Apply feed multiplier adjustment
    const baseDailyFeed = Math.round((estimatedWeight * 0.06)); // 6% of body weight
    const dailyFeedPerChicken = Math.round(baseDailyFeed * feedMultiplier);
    const weeklyFeedPerChicken = dailyFeedPerChicken * 7;
    const totalWeeklyFeed = weeklyFeedPerChicken * chickenCount;

    // Add weight-specific recommendations
    if (weight && weight < expectedWeight * 0.85) {
        recommendations.unshift(`⚠️ UNDERWEIGHT: Current ${weight}g vs Target ${expectedWeight}g (${Math.round((1 - weight/expectedWeight) * 100)}% below)`);
        recommendations.unshift(`📈 Feed increased by 15% (${dailyFeedPerChicken}g/day) and protein boosted to ${nutritionPlan.protein}% to accelerate growth`);
        recommendations.push('Consider supplementing with high-energy treats (mealworms, scratch grains)');
        recommendations.push('Monitor daily - birds may be stressed or ill');
    } else if (weight && weight > expectedWeight * 1.15) {
        recommendations.unshift(`⚠️ OVERWEIGHT: Current ${weight}g vs Target ${expectedWeight}g (${Math.round((weight/expectedWeight - 1) * 100)}% above)`);
        recommendations.unshift(`📉 Feed reduced by 20% (${dailyFeedPerChicken}g/day) and protein lowered to ${nutritionPlan.protein}% to control growth`);
        recommendations.push('Encourage more activity and foraging');
        recommendations.push('Next week target: slower growth to avoid obesity');
    } else if (weight) {
        recommendations.unshift(`✓ OPTIMAL: Weight ${weight}g is on target for week ${ageInWeeks} (${expectedWeight}g expected)`);
        recommendations.unshift(`✓ Standard feeding: ${dailyFeedPerChicken}g/day with ${nutritionPlan.protein}% protein`);
    }

    return {
        growthStage,
        nutritionPlan,
        dailyFeedPerChicken,
        weeklyFeedPerChicken,
        totalWeeklyFeed,
        ingredients,
        recommendations,
        feedAdjustment: feedMultiplier, // Return the multiplier for reference
        weightStatus: weightRatio > 1.15 ? 'overweight' : weightRatio < 0.85 ? 'underweight' : 'optimal'
    };
}

// POST - Generate feed plan for a flock
router.post('/generate', async (req, res) => {
    try {
        const { flockId, currentWeight, actualWeight, predictedWeight } = req.body;

        // Validation
        if (!flockId) {
            return res.status(400).json({
                success: false,
                error: 'Please provide flockId'
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

        // Get current week number (check existing feed plans)
        const lastPlan = await FeedPlan.findOne({ flock: flockId })
            .sort({ weekNumber: -1 });
        
        const weekNumber = lastPlan ? lastPlan.weekNumber + 1 : 1;

        // Use actual weight if available, otherwise use current weight
        const weightToUse = actualWeight || currentWeight;
        
        console.log('Feed Plan Generation:', {
            actualWeight,
            predictedWeight,
            weightToUse,
            age: flock.ageInWeeks
        });

        // Generate feed plan with both actual and predicted weights
        const planData = generateFeedPlan(
            flock.ageInWeeks,
            weightToUse,
            flock.currentCount,
            flock.breed,
            predictedWeight
        );

        // Create feed plan document
        const feedPlan = new FeedPlan({
            flock: flockId,
            weekNumber: weekNumber,
            currentAge: flock.ageInWeeks,
            currentWeight: weightToUse || planData.estimatedWeight,
            growthStage: planData.growthStage,
            nutritionPlan: planData.nutritionPlan,
            dailyFeedPerChicken: planData.dailyFeedPerChicken,
            weeklyFeedPerChicken: planData.weeklyFeedPerChicken,
            totalWeeklyFeed: planData.totalWeeklyFeed,
            ingredients: planData.ingredients,
            recommendations: planData.recommendations
        });

        await feedPlan.save();

        // Return feed plan
        res.status(201).json({
            success: true,
            message: 'Feed plan generated successfully',
            data: {
                flock: {
                    id: flock._id,
                    name: flock.name,
                    breed: flock.breed,
                    ageInWeeks: flock.ageInWeeks,
                    currentCount: flock.currentCount
                },
                plan: {
                    weekNumber: weekNumber,
                    growthStage: planData.growthStage,
                    nutritionPlan: planData.nutritionPlan,
                    feedingDetails: {
                        dailyPerChicken: `${planData.dailyFeedPerChicken}g`,
                        weeklyPerChicken: `${planData.weeklyFeedPerChicken}g`,
                        totalWeeklyFeed: `${(planData.totalWeeklyFeed / 1000).toFixed(2)}kg`
                    },
                    ingredients: {
                        corn: `${planData.ingredients.corn}%`,
                        soybeanMeal: `${planData.ingredients.soybeanMeal}%`,
                        wheat: `${planData.ingredients.wheat}%`,
                        vitamins: `${planData.ingredients.vitamins}%`,
                        minerals: `${planData.ingredients.minerals}%`
                    },
                    recommendations: planData.recommendations
                },
                planId: feedPlan._id
            }
        });

    } catch (error) {
        console.error('Feed Plan Error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// GET - Get all feed plans for a flock
router.get('/:flockId', async (req, res) => {
    try {
        const feedPlans = await FeedPlan.find({ flock: req.params.flockId })
            .sort({ weekNumber: -1 })
            .populate('flock', 'name breed currentCount');

        if (!feedPlans || feedPlans.length === 0) {
            return res.status(404).json({
                success: false,
                error: 'No feed plans found for this flock'
            });
        }

        res.json({
            success: true,
            count: feedPlans.length,
            data: feedPlans
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// GET - Get latest feed plan for a flock
router.get('/:flockId/latest', async (req, res) => {
    try {
        const feedPlan = await FeedPlan.findOne({ flock: req.params.flockId })
            .sort({ weekNumber: -1 })
            .populate('flock', 'name breed ageInWeeks currentCount');

        if (!feedPlan) {
            return res.status(404).json({
                success: false,
                error: 'No feed plans found for this flock'
            });
        }

        res.json({
            success: true,
            data: feedPlan
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

module.exports = router;
