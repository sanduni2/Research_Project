const axios = require('axios');

const API_URL = 'http://localhost:3000/api';
const ML_SERVICE_URL = 'http://localhost:5000/api';

console.log('='.repeat(60));
console.log('🧪 Testing Integrated Farm System API');
console.log('='.repeat(60));

async function testHealth() {
    console.log('\n1️⃣ Testing Health Endpoints...');
    
    try {
        const backendHealth = await axios.get(`${API_URL}/health`);
        console.log('   ✅ Backend API:', backendHealth.data.message);
    } catch (error) {
        console.log('   ❌ Backend API Error:', error.message);
        return false;
    }

    try {
        const mlHealth = await axios.get(`${ML_SERVICE_URL}/health`);
        console.log('   ✅ ML Service:', mlHealth.data.message);
    } catch (error) {
        console.log('   ❌ ML Service Error:', error.message);
        return false;
    }

    return true;
}

async function testCreateFlock() {
    console.log('\n2️⃣ Testing Flock Creation...');
    
    try {
        const response = await axios.post(`${API_URL}/flocks`, {
            name: 'Test Flock',
            breed: 'Rhode Island Red',
            initialCount: 100,
            ageInWeeks: 4,
            notes: 'Test flock created by API test script'
        });

        if (response.data.success) {
            console.log('   ✅ Flock created:', response.data.data.name);
            console.log('   📋 Flock ID:', response.data.data._id);
            return response.data.data;
        }
    } catch (error) {
        console.log('   ❌ Flock Creation Error:', error.response?.data?.error || error.message);
        return null;
    }
}

async function testWeightPrediction() {
    console.log('\n3️⃣ Testing Weight Prediction...');
    
    try {
        const response = await axios.post(`${ML_SERVICE_URL}/predict/weight`, {
            age: 28  // 4 weeks = 28 days
        });

        if (response.data.success) {
            console.log('   ✅ Weight predicted:', response.data.predicted_weight, 'grams');
            console.log('   📅 For age:', response.data.age_in_days, 'days');
            return response.data.predicted_weight;
        }
    } catch (error) {
        console.log('   ❌ Weight Prediction Error:', error.response?.data?.error || error.message);
        return null;
    }
}

async function testGrowthPrediction(flockId) {
    console.log('\n4️⃣ Testing Growth Prediction (without image)...');
    
    try {
        const FormData = require('form-data');
        const formData = new FormData();
        formData.append('flockId', flockId);
        formData.append('actualWeight', '450');
        formData.append('feedType', 'Starter Feed');
        formData.append('weekNumber', '4');

        const response = await axios.post(
            `${API_URL}/predictions/growth`,
            formData,
            {
                headers: formData.getHeaders()
            }
        );

        if (response.data.success) {
            console.log('   ✅ Prediction completed');
            console.log('   📊 Predicted Weight:', response.data.data.prediction.predictedWeight, 'g');
            console.log('   ⚖️ Actual Weight:', response.data.data.prediction.actualWeight, 'g');
            console.log('   📈 Growth Status:', response.data.data.prediction.growthStatus);
            console.log('   🍽️ Feed Consumed:', response.data.data.feedAnalysis.feedConsumedPercentage, '%');
            return response.data.data;
        }
    } catch (error) {
        console.log('   ❌ Growth Prediction Error:', error.response?.data?.error || error.message);
        return null;
    }
}

async function testFeedPlan(flockId) {
    console.log('\n5️⃣ Testing Feed Plan Generation...');
    
    try {
        const response = await axios.post(`${API_URL}/feed-plans/generate`, {
            flockId: flockId,
            currentWeight: 450
        });

        if (response.data.success) {
            const plan = response.data.data.plan;
            console.log('   ✅ Feed plan generated');
            console.log('   🌱 Growth Stage:', plan.growthStage);
            console.log('   🥗 Protein:', plan.nutritionPlan.protein, '%');
            console.log('   ⚖️ Daily Feed:', plan.feedingDetails.dailyPerChicken);
            console.log('   📦 Weekly Total:', plan.feedingDetails.totalWeeklyFeed);
            return response.data.data;
        }
    } catch (error) {
        console.log('   ❌ Feed Plan Error:', error.response?.data?.error || error.message);
        return null;
    }
}

async function testGetAllFlocks() {
    console.log('\n6️⃣ Testing Get All Flocks...');
    
    try {
        const response = await axios.get(`${API_URL}/flocks`);

        if (response.data.success) {
            console.log('   ✅ Found', response.data.count, 'flock(s)');
            response.data.data.forEach((flock, index) => {
                console.log(`   ${index + 1}. ${flock.name} (${flock.breed}) - ${flock.currentCount} chickens`);
            });
            return response.data.data;
        }
    } catch (error) {
        console.log('   ❌ Get Flocks Error:', error.response?.data?.error || error.message);
        return null;
    }
}

async function testCleanup(flockId) {
    console.log('\n7️⃣ Cleaning up test data...');
    
    try {
        await axios.delete(`${API_URL}/flocks/${flockId}`);
        console.log('   ✅ Test flock deleted');
    } catch (error) {
        console.log('   ⚠️ Cleanup warning:', error.message);
    }
}

async function runAllTests() {
    console.log('\n🏃 Starting tests...\n');

    // Test 1: Health checks
    const healthOk = await testHealth();
    if (!healthOk) {
        console.log('\n❌ Health checks failed. Please ensure both services are running:');
        console.log('   1. ML Service: cd ml_service && python app.py');
        console.log('   2. Backend API: npm start');
        return;
    }

    // Test 2: Create flock
    const flock = await testCreateFlock();
    if (!flock) {
        console.log('\n❌ Cannot continue tests without a flock');
        return;
    }

    // Test 3: Weight prediction
    await testWeightPrediction();

    // Test 4: Growth prediction
    await testGrowthPrediction(flock._id);

    // Test 5: Feed plan
    await testFeedPlan(flock._id);

    // Test 6: Get all flocks
    await testGetAllFlocks();

    // Test 7: Cleanup
    await testCleanup(flock._id);

    console.log('\n' + '='.repeat(60));
    console.log('✅ All tests completed successfully!');
    console.log('='.repeat(60));
    console.log('\n📱 You can now test the mobile app:');
    console.log('   cd Integrated-Farm-System-Frontend');
    console.log('   npm start');
    console.log('\n');
}

// Run tests
runAllTests().catch(error => {
    console.error('\n💥 Test suite error:', error.message);
    process.exit(1);
});
