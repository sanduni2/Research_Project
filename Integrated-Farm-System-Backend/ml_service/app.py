from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Load models
print("Loading models...")

# Path to models directory - use absolute path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'data_anaysis', 'models')
print(f"Looking for models in: {MODELS_DIR}")

# Load weight prediction model - NEW BROILER MODEL (0-12 weeks)
try:
    weight_model = joblib.load(os.path.join(MODELS_DIR, 'broiler_weight_prediction.pkl'))
    weight_scaler = joblib.load(os.path.join(MODELS_DIR, 'broiler_weight_scaler.pkl'))
    print("✅ Broiler weight prediction model loaded successfully (0-12 weeks)")
except Exception as e:
    print(f"❌ Error loading broiler weight model: {e}")
    # Fallback to old model
    try:
        weight_model = joblib.load(os.path.join(MODELS_DIR, 'weight_prediction_linear_regression.pkl'))
        weight_scaler = joblib.load(os.path.join(MODELS_DIR, 'weight_prediction_scaler.pkl'))
        print("⚠️  Using fallback weight prediction model (0-3 weeks only)")
    except Exception as e2:
        print(f"❌ Error loading fallback model: {e2}")
        weight_model = None
        weight_scaler = None

# Load ResNet50 image classification model
try:
    resnet_model_path = os.path.join(MODELS_DIR, 'resnet50', 'best_model.h5')
    resnet_model = load_model(resnet_model_path, compile=False)
    print("✅ ResNet50 image classification model loaded successfully")
except Exception as e:
    print(f"⚠️  ResNet50 model not loaded: {str(e)[:100]}")
    print("   Weight prediction will still work!")
    resnet_model = None

# Class labels for feed consumption (0%, 25%, 50%, 100%)
CLASS_LABELS = [0, 25, 50, 100]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'ML Service is running',
        'models': {
            'weight_prediction': weight_model is not None,
            'image_classification': resnet_model is not None
        }
    })

@app.route('/api/predict/weight', methods=['POST'])
def predict_weight():
    """Predict chicken weight from age in days using Broiler Growth Model (0-12 weeks)"""
    try:
        data = request.get_json()
        
        if 'age' not in data:
            return jsonify({
                'success': False,
                'error': 'Please provide age in days'
            }), 400
        
        if weight_model is None or weight_scaler is None:
            return jsonify({
                'success': False,
                'error': 'Weight prediction model not available'
            }), 503
        
        age = float(data['age'])
        
        # Get diet type (default to 'Standard' if not provided)
        diet_type = data.get('diet', 'Standard')
        
        # Encode diet type (High_Protein=0, Low_Protein=1, Standard=2 based on LabelEncoder)
        diet_mapping = {'High_Protein': 0, 'Low_Protein': 1, 'Standard': 2}
        diet_encoded = diet_mapping.get(diet_type, 2)  # Default to Standard
        
        # Create features matching training: Age_Days, Age_Squared, Age_Cubed, Diet_Encoded, Age_Diet_Interaction
        age_squared = age ** 2
        age_cubed = age ** 3
        age_diet_interaction = age * diet_encoded
        
        features = np.array([[age, age_squared, age_cubed, diet_encoded, age_diet_interaction]])
        
        # Scale features
        features_scaled = weight_scaler.transform(features)
        
        # Predict
        predicted_weight = weight_model.predict(features_scaled)[0]
        
        # Ensure non-negative weight
        predicted_weight = max(0, predicted_weight)
        
        # Calculate age in weeks for display
        age_in_weeks = age / 7
        
        return jsonify({
            'success': True,
            'age_in_days': age,
            'age_in_weeks': round(age_in_weeks, 1),
            'predicted_weight': round(float(predicted_weight), 2),
            'diet_type': diet_type,
            'unit': 'grams'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/predict/feed-consumption', methods=['POST'])
def predict_feed_consumption():
    """Classify feed consumption percentage from image (0%, 25%, 50%, 100%)"""
    try:
        if resnet_model is None:
            return jsonify({
                'success': False,
                'error': 'Image classification model not available'
            }), 503
        
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image file selected'
            }), 400
        
        # Read and preprocess image
        img = Image.open(io.BytesIO(file.read()))
        img = img.convert('RGB')
        img = img.resize((224, 224))  # ResNet50 input size
        
        # Convert to array and preprocess
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Normalize to [0, 1]
        
        # Predict
        predictions = resnet_model.predict(img_array)
        predicted_class_idx = np.argmax(predictions[0])
        predicted_percentage = CLASS_LABELS[predicted_class_idx]
        confidence = float(predictions[0][predicted_class_idx])
        
        # Get all class probabilities
        class_probabilities = {
            f"{CLASS_LABELS[i]}%": float(predictions[0][i])
            for i in range(len(CLASS_LABELS))
        }
        
        return jsonify({
            'success': True,
            'predicted_percentage': predicted_percentage,
            'confidence': round(confidence * 100, 2),
            'class_probabilities': class_probabilities
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/predict/batch', methods=['POST'])
def predict_batch():
    """Predict both weight and feed consumption in one request"""
    try:
        # Get age for weight prediction
        age = float(request.form.get('age', 0))
        
        # Predict weight
        if age > 0 and weight_model is not None:
            features = np.array([[age, age**2, age**3]])
            features_scaled = weight_scaler.transform(features)
            predicted_weight = max(0, weight_model.predict(features_scaled)[0])
        else:
            predicted_weight = None
        
        # Predict feed consumption from image
        feed_percentage = None
        if 'image' in request.files and resnet_model is not None:
            file = request.files['image']
            if file.filename != '':
                img = Image.open(io.BytesIO(file.read()))
                img = img.convert('RGB')
                img = img.resize((224, 224))
                img_array = image.img_to_array(img)
                img_array = np.expand_dims(img_array, axis=0)
                img_array = img_array / 255.0
                predictions = resnet_model.predict(img_array)
                predicted_class_idx = np.argmax(predictions[0])
                feed_percentage = CLASS_LABELS[predicted_class_idx]
        
        return jsonify({
            'success': True,
            'weight_prediction': {
                'age_in_days': age,
                'predicted_weight': round(float(predicted_weight), 2) if predicted_weight else None,
                'unit': 'grams'
            },
            'feed_prediction': {
                'predicted_percentage': feed_percentage
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting ML Service on http://localhost:5000")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
