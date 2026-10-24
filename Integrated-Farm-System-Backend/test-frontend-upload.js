/**
 * Test frontend-style file upload
 * This simulates how React Native sends files
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const BACKEND_URL = 'http://localhost:3000';

async function testFrontendStyleUpload() {
    console.log('='  .repeat(60));
    console.log('🧪 TESTING FRONTEND-STYLE FILE UPLOAD');
    console.log('='  .repeat(60));

    // Get a test image
    const testImageDir = path.join(__dirname, '../data_anaysis/data/50_percent');
    const files = fs.readdirSync(testImageDir).filter(f => 
        f.toLowerCase().match(/\.(jpg|jpeg|png)$/)
    );

    if (files.length === 0) {
        console.log('❌ No test images found');
        return;
    }

    const testImagePath = path.join(testImageDir, files[0]);
    console.log(`\n📷 Using test image: ${testImagePath}`);

    try {
        // Test 1: Basic upload test
        console.log('\n--- Test 1: Debug Endpoint ---');
        const formData1 = new FormData();
        formData1.append('feedImage', fs.createReadStream(testImagePath));
        formData1.append('testField', 'test value');

        const response1 = await axios.post(
            `${BACKEND_URL}/api/predictions/test-upload`,
            formData1,
            {
                headers: formData1.getHeaders(),
                timeout: 10000
            }
        );

        console.log('✅ Response:', JSON.stringify(response1.data, null, 2));

        // Test 2: Full prediction endpoint
        console.log('\n--- Test 2: Full Prediction Endpoint ---');
        
        // First, we need a flock ID - let's get one
        const flocksResponse = await axios.get(`${BACKEND_URL}/api/flocks`);
        if (!flocksResponse.data.success || flocksResponse.data.data.length === 0) {
            console.log('⚠️  No flocks available for testing');
            return;
        }

        const testFlock = flocksResponse.data.data[0];
        console.log(`Using flock: ${testFlock.name} (${testFlock._id})`);

        const formData2 = new FormData();
        formData2.append('flockId', testFlock._id);
        formData2.append('feedType', 'Starter Feed');
        formData2.append('weekNumber', testFlock.ageInWeeks);
        formData2.append('actualWeight', '500');
        formData2.append('feedImage', fs.createReadStream(testImagePath));

        console.log('Sending request...');
        const response2 = await axios.post(
            `${BACKEND_URL}/api/predictions/growth`,
            formData2,
            {
                headers: formData2.getHeaders(),
                timeout: 30000
            }
        );

        console.log('\n✅ Prediction Response:');
        console.log(`   Success: ${response2.data.success}`);
        if (response2.data.data) {
            console.log(`   Predicted Weight: ${response2.data.data.prediction.predictedWeight}g`);
            console.log(`   Feed Consumption: ${response2.data.data.feedAnalysis.feedConsumedPercentage}%`);
            console.log(`   Growth Status: ${response2.data.data.prediction.growthStatus || 'N/A'}`);
        }

    } catch (error) {
        console.error('\n❌ ERROR:', error.message);
        if (error.response) {
            console.error('Response Status:', error.response.status);
            console.error('Response Data:', JSON.stringify(error.response.data, null, 2));
        }
    }

    console.log('\n' + '='  .repeat(60));
}

// Run test
testFrontendStyleUpload().catch(console.error);
