# 🔄 Model Retraining Guide

## Problem Summary

Your current feed consumption model has accuracy issues:
- ✅ **0% (Empty):** 100% accurate
- ✅ **100% (Full):** 65-92% accurate  
- ❌ **25%:** Only 0-70% accurate (often predicts 100%)
- ❌ **50%:** Only 30-50% accurate (often predicts 100%)

## Solution

Retrain the model with improved techniques to achieve **>80% accuracy** for all classes.

---

## 🚀 Quick Start (15-30 minutes)

### Step 1: Activate Virtual Environment
```powershell
cd D:\Research
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install Required Packages (if needed)
```powershell
pip install tensorflow scikit-learn matplotlib seaborn
```

### Step 3: Run Improved Training
```powershell
cd data_anaysis
python retrain_feed_model_improved.py
```

**Expected output:**
- Phase 1 training: ~10-15 minutes (frozen base)
- Phase 2 fine-tuning: ~10-20 minutes (unfrozen layers)
- Total: **15-35 minutes** depending on hardware

### Step 4: Review Results

Check the generated report:
- `models/resnet50/training_results_improved.png` - Visual performance charts
- `models/resnet50/best_model_improved_metadata.json` - Accuracy metrics

**Look for:**
- Test accuracy > 85%
- Per-class accuracy > 80% for all classes (especially 25% and 50%)

### Step 5: Deploy the Improved Model
```powershell
python deploy_improved_model.py
```

This will:
- Backup your current model
- Replace it with the improved version
- Copy to your ML service directory

### Step 6: Restart Services
```powershell
# Terminal 1 - ML Service
cd ..\Integrated-Farm-System-Backend\ml_service
python app.py

# Terminal 2 - Backend
cd ..\Integrated-Farm-System-Backend
node server.js

# Terminal 3 - Frontend
cd ..\Integrated-Farm-System-Frontend
npx expo start
```

---

## 🔍 What the Improved Training Does

### 1. **Enhanced Data Augmentation**
```python
• Rotation: ±25° (was ±20°)
• Position shift: ±25% (was ±20%)
• Brightness: 70%-130% (NEW - critical for feed images!)
• Zoom: ±25% (was ±20%)
• Shear: ±15%
• Horizontal flip
```

**Why this helps:** Feed plate lighting varies a lot in real conditions. Brightness augmentation helps the model handle different lighting.

### 2. **Class Weights**
Automatically balances training if some classes have more images:
```python
0%: weight=1.2
25%: weight=1.5  ← More focus on problematic class
50%: weight=1.5  ← More focus on problematic class
100%: weight=1.0
```

### 3. **Two-Phase Training**
- **Phase 1 (20 epochs):** Train only top layers (base frozen)
- **Phase 2 (30 epochs):** Fine-tune entire network (base unfrozen)

**Why this helps:** Prevents catastrophic forgetting of ImageNet features.

### 4. **Smart Callbacks**
- **Early Stopping:** Stops if no improvement (patience=10)
- **Learning Rate Reduction:** Reduces LR when stuck (factor=0.5)
- **Best Model Checkpoint:** Saves only the best version

---

## 📊 Reading the Results

After training, you'll see:

### Console Output
```
✅ RETRAINING COMPLETE!
====================================
📊 Final Results:
   Overall Test Accuracy: 92.50%
   
   Per-Class Results:
      ✅    0%:  98.00%
      ✅   25%:  87.50%  ← Should be >80% now!
      ✅   50%:  89.00%  ← Should be >80% now!
      ✅  100%:  95.50%
```

### Visual Report (`training_results_improved.png`)
- **Top-left:** Training progress (accuracy over time)
- **Top-right:** Loss curves
- **Bottom-left:** Confusion matrix (where mistakes happen)
- **Bottom-right:** Per-class accuracy bars

### What "Good" Looks Like
✅ **Good results:**
- Overall accuracy > 85%
- All classes > 80%
- Confusion matrix mostly diagonal
- Green bars in per-class chart

⚠️ **Needs more work:**
- Any class < 70%
- High confusion between 25% ↔ 50%
- Red/orange bars in chart

---

## 🧪 Testing the Improved Model

### Test with Problem Images
```powershell
cd ..\Integrated-Farm-System-Backend
node test-image-upload.js
```

Or test specific image:
```powershell
node -e "const FormData = require('form-data'); const fs = require('fs'); const axios = require('axios'); async function test() { const formData = new FormData(); formData.append('image', fs.createReadStream('D:/Research/data_anaysis/data/25_percent/25_percent_36.jpg')); const r = await axios.post('http://localhost:5000/api/predict/feed-consumption', formData, { headers: formData.getHeaders() }); console.log('Predicted:', r.data.predicted_percentage + '%'); console.log('Confidence:', r.data.confidence.toFixed(1) + '%'); console.log('Expected: 25% plate → 75% consumption'); } test();"
```

**Expected improvements:**
- `25_percent_36.jpg`: Was 50% confidence → Should be >70% now
- `25_percent` images: Was often 100% → Should mostly be 25% now
- `50_percent` images: Was often 100% → Should mostly be 50% now

---

## 🔧 Troubleshooting

### Training Takes Too Long
**Reduce epochs:** Edit `retrain_feed_model_improved.py`
```python
# Line 75
EPOCHS = 30  # Reduce from 50
```

### Out of Memory Error
**Reduce batch size:** Edit `retrain_feed_model_improved.py`
```python
# Line 74
BATCH_SIZE = 8  # Reduce from 16
```

### Accuracy Still Too Low (<80%)
**Try these:**

1. **Collect more diverse images:**
   ```
   - Different lighting conditions
   - Multiple camera angles  
   - Various feed types
   - Different plate materials
   ```

2. **Increase training time:**
   ```python
   EPOCHS = 100  # More epochs
   ```

3. **Try different architecture:**
   Replace ResNet50 with EfficientNetB0 (more efficient):
   ```python
   from tensorflow.keras.applications import EfficientNetB0
   base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(*IMAGE_SIZE, 3))
   ```

### Model Got Worse
**Restore backup:**
```powershell
cd data_anaysis
# Find backup in models/resnet50/backups/
# Copy it back
cp models/resnet50/backups/best_model_backup_YYYYMMDD_HHMMSS.h5 models/resnet50/best_model.h5
```

---

## 📈 Expected Timeline & Results

### Timeline
| Task | Duration |
|------|----------|
| Setup & installation | 5 min |
| Training (Phase 1) | 10-15 min |
| Fine-tuning (Phase 2) | 10-20 min |
| Deployment | 2 min |
| Testing | 5 min |
| **Total** | **30-45 min** |

### Expected Results
| Class | Before | Target | Achievable |
|-------|--------|--------|------------|
| 0% | 100% ✅ | 100% | 98-100% |
| 25% | 0-70% ❌ | >80% | 85-95% |
| 50% | 30-50% ❌ | >80% | 85-93% |
| 100% | 65-92% ⚠️ | >85% | 92-98% |

---

## 🎯 Next Steps After Successful Retraining

1. **Update your app's confidence threshold:**
   - Currently rejects predictions <60%
   - With improved model, you can lower to <50%

2. **Remove the confidence warning for good predictions:**
   - Warnings only for <50% confidence
   - Better user experience

3. **Document the improved accuracy:**
   - Update your project README
   - Include before/after metrics
   - Show the improvements in your demo

4. **Consider A/B testing:**
   - Keep old model as backup
   - Compare real-world performance
   - Get user feedback

---

## 📞 Need Help?

**Common issues and solutions are in this guide.**

If accuracy is still below target after retraining:
1. Check if you have enough training images (recommended: >300 per class)
2. Verify image quality (not blurry, good lighting)
3. Consider simplifying to 2-class model (0% vs 100% only)

---

## 📝 Summary

✅ **Run:** `python retrain_feed_model_improved.py`  
✅ **Wait:** 15-30 minutes  
✅ **Deploy:** `python deploy_improved_model.py`  
✅ **Test:** Upload images in your app  
✅ **Enjoy:** Better accuracy! 🎉

**Key improvements:**
- Brightness augmentation (handles lighting variations)
- Class weights (focuses on problematic 25%/50%)
- Two-phase training (better feature learning)
- Smart callbacks (prevents overfitting)

**Target:** **>80% accuracy for ALL classes** 🎯
