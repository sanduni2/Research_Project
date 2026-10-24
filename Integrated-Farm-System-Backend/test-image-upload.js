/**
 * Test script to verify image upload from backend to ML service
 * Run with: node test-image-upload.js
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const ML_SERVICE_URL = 'http://localhost:5000';

// Test with a sample image from each category
const testImages = [
    {
        category: '0%',
        path: '../data_anaysis/data/0_percent'
    },
    {
        category: '25%',
        path: '../data_anaysis/data/25_percent'
    },
    {
        category: '50%',
        path: '../data_anaysis/data/50_percent'
    },
    {
        category: '100%',
        path: '../data_anaysis/data/100_percent'
    }
];

async function testImageUpload(category, imagePath) {
    try {
        console.log(`\n🧪 Testing ${category} category...`);
        console.log(`   Image: ${imagePath}`);
        
        const formData = new FormData();
        formData.append('image', fs.createReadStream(imagePath));

        const response = await axios.post(
            `${ML_SERVICE_URL}/api/predict/feed-consumption`,
            formData,
            {
                headers: formData.getHeaders(),
                timeout: 30000
            }
        );

        const predicted = response.data.predicted_percentage;
        const confidence = response.data.confidence;
        const isCorrect = predicted === parseInt(category.replace('%', ''));

        console.log(`   ✅ Result: ${predicted}% (confidence: ${confidence}%)`);
        console.log(`   ${isCorrect ? '✓ CORRECT' : '✗ INCORRECT'}`);
        
        return {
            category,
            predicted,
            confidence,
            correct: isCorrect
        };

    } catch (error) {
        console.error(`   ❌ ERROR: ${error.message}`);
        if (error.response) {
            console.error(`   Response: ${JSON.stringify(error.response.data)}`);
        }
        return {
            category,
            error: error.message
        };
    }
}

async function runTests() {
    console.log('='  .repeat(60));
    console.log('🔬 BACKEND TO ML SERVICE IMAGE UPLOAD TEST');
    console.log('='  .repeat(60));

    const results = [];

    for (const test of testImages) {
        const fullPath = path.join(__dirname, test.path);
        
        // Check if directory exists
        if (!fs.existsSync(fullPath)) {
            console.log(`\n⚠️  Directory not found: ${fullPath}`);
            continue;
        }

        // Get first image file
        const files = fs.readdirSync(fullPath).filter(f => 
            f.toLowerCase().match(/\.(jpg|jpeg|png)$/)
        );

        if (files.length === 0) {
            console.log(`\n⚠️  No images found in: ${fullPath}`);
            continue;
        }

        const imagePath = path.join(fullPath, files[0]);
        const result = await testImageUpload(test.category, imagePath);
        results.push(result);
    }

    // Summary
    console.log('\n' + '='  .repeat(60));
    console.log('📊 TEST SUMMARY');
    console.log('='  .repeat(60));
    
    const correct = results.filter(r => r.correct).length;
    const total = results.filter(r => !r.error).length;
    
    console.log(`Accuracy: ${correct}/${total} (${(correct/total*100).toFixed(1)}%)`);
    console.log('\nDetailed Results:');
    results.forEach(r => {
        if (r.error) {
            console.log(`  ${r.category}: ERROR - ${r.error}`);
        } else {
            console.log(`  ${r.category}: Predicted ${r.predicted}% (${r.confidence}% conf) ${r.correct ? '✓' : '✗'}`);
        }
    });
    console.log('='  .repeat(60));
}

// Run tests
runTests().catch(console.error);
