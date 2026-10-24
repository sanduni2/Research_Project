"""
DEPLOY IMPROVED MODEL
Replaces the current model with the improved version after verification
"""

import os
import shutil
import json
from datetime import datetime

print("="*80)
print("🚀 DEPLOYING IMPROVED FEED CONSUMPTION MODEL")
print("="*80)

# Paths
OLD_MODEL = 'models/resnet50/best_model.h5'
NEW_MODEL = 'models/resnet50/best_model_improved.h5'
BACKUP_DIR = 'models/resnet50/backups'
ML_SERVICE_MODEL = '../Integrated-Farm-System-Backend/ml_service/models/resnet50/best_model.h5'

# =====================================
# STEP 1: VERIFY NEW MODEL EXISTS
# =====================================
print("\n✅ Step 1: Verifying improved model exists...")
if not os.path.exists(NEW_MODEL):
    print(f"   ❌ ERROR: Improved model not found at {NEW_MODEL}")
    print(f"   Please run retrain_feed_model_improved.py first!")
    exit(1)

print(f"   ✅ Found: {NEW_MODEL}")

# Check metadata
metadata_path = 'models/resnet50/best_model_improved_metadata.json'
if os.path.exists(metadata_path):
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    print(f"\n📊 New Model Stats:")
    print(f"   Test Accuracy: {metadata.get('test_accuracy', 0)*100:.2f}%")
    print(f"   Training Images: {metadata.get('training_images', 0)}")
    print(f"   Total Epochs: {metadata.get('epochs_phase1', 0) + metadata.get('epochs_phase2', 0)}")

# =====================================
# STEP 2: BACKUP OLD MODEL
# =====================================
print("\n💾 Step 2: Backing up current model...")
os.makedirs(BACKUP_DIR, exist_ok=True)

if os.path.exists(OLD_MODEL):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f'best_model_backup_{timestamp}.h5')
    shutil.copy2(OLD_MODEL, backup_path)
    print(f"   ✅ Backed up to: {backup_path}")
else:
    print(f"   ⚠️  No existing model to backup")

# =====================================
# STEP 3: REPLACE WITH IMPROVED MODEL
# =====================================
print("\n🔄 Step 3: Deploying improved model...")

# Copy to main location
shutil.copy2(NEW_MODEL, OLD_MODEL)
print(f"   ✅ Copied to: {OLD_MODEL}")

# Copy to ML service if path exists
ml_service_dir = os.path.dirname(ML_SERVICE_MODEL)
if os.path.exists(os.path.dirname(ml_service_dir)):
    os.makedirs(ml_service_dir, exist_ok=True)
    shutil.copy2(NEW_MODEL, ML_SERVICE_MODEL)
    print(f"   ✅ Copied to ML service: {ML_SERVICE_MODEL}")
else:
    print(f"   ⚠️  ML service path not found (this is okay if running from different location)")

# =====================================
# STEP 4: VERIFY DEPLOYMENT
# =====================================
print("\n✅ Step 4: Verifying deployment...")

if os.path.exists(OLD_MODEL):
    old_size = os.path.getsize(OLD_MODEL) / (1024 * 1024)  # MB
    new_size = os.path.getsize(NEW_MODEL) / (1024 * 1024)  # MB
    print(f"   ✅ Model deployed successfully!")
    print(f"   Size: {old_size:.1f} MB")
    
    if abs(old_size - new_size) < 0.1:
        print(f"   ✅ File sizes match")
    else:
        print(f"   ⚠️  Size mismatch (expected {new_size:.1f} MB)")

# =====================================
# FINAL INSTRUCTIONS
# =====================================
print("\n" + "="*80)
print("✅ DEPLOYMENT COMPLETE!")
print("="*80)

print("\n📋 Next Steps:")
print("   1. Restart your ML service:")
print("      cd ../Integrated-Farm-System-Backend/ml_service")
print("      python app.py")
print("\n   2. Restart your backend:")
print("      cd ../Integrated-Farm-System-Backend")
print("      node server.js")
print("\n   3. Test with previously problematic images:")
print("      - Upload 25_percent_50.jpg should show ~75% consumption")
print("      - Upload 25_percent_36.jpg should have better confidence now")
print("\n   4. If issues occur, restore backup:")
print(f"      cp {backup_path} {OLD_MODEL}")

print("\n💡 Expected Improvements:")
print("   - Higher accuracy for 25% class (target: >80%)")
print("   - Higher accuracy for 50% class (target: >80%)")
print("   - Better confidence scores overall")
print("   - Fewer misclassifications as 100%")

print("\n" + "="*80)
