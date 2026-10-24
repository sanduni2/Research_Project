"""
IMPROVED FEED CONSUMPTION MODEL RETRAINING
Fixes accuracy issues with 25% and 50% feed level predictions

Improvements:
- Enhanced data augmentation (brightness, contrast, lighting variations)
- Class weights to handle any imbalance
- Learning rate scheduling
- Early stopping with best model restoration
- Detailed per-class evaluation
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

print("="*80)
print("🔄 RETRAINING FEED CONSUMPTION MODEL - Improved Version")
print("="*80)

# =====================================
# CONFIGURATION
# =====================================
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16  # Smaller batch size for better generalization
EPOCHS = 50
LEARNING_RATE = 0.0001
CLASS_NAMES = ['0%', '25%', '50%', '100%']
DATA_DIR = 'data'

print(f"\n⚙️ Configuration:")
print(f"   Image Size: {IMAGE_SIZE}")
print(f"   Batch Size: {BATCH_SIZE}")
print(f"   Max Epochs: {EPOCHS}")
print(f"   Learning Rate: {LEARNING_RATE}")
print(f"   Classes: {CLASS_NAMES}")

# =====================================
# STEP 1: LOAD AND PREPARE DATA
# =====================================
print("\n📂 Step 1: Loading Images...")

def load_images_from_folders(data_dir, class_names):
    """Load images from class folders"""
    X = []
    y = []
    
    for class_idx, class_name in enumerate(class_names):
        folder = class_name.replace('%', '_percent')
        folder_path = os.path.join(data_dir, folder)
        
        if not os.path.exists(folder_path):
            print(f"   ⚠️  Folder not found: {folder_path}")
            continue
        
        images = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
        print(f"   ✅ {class_name}: {len(images)} images")
        
        for img_name in images:
            img_path = os.path.join(folder_path, img_name)
            try:
                # Load and preprocess image
                img = tf.keras.preprocessing.image.load_img(
                    img_path, 
                    target_size=IMAGE_SIZE
                )
                img_array = tf.keras.preprocessing.image.img_to_array(img)
                X.append(img_array)
                y.append(class_idx)
            except Exception as e:
                print(f"   ⚠️  Error loading {img_name}: {e}")
    
    return np.array(X), np.array(y)

# Load data
X, y = load_images_from_folders(DATA_DIR, CLASS_NAMES)
print(f"\n✅ Total images loaded: {len(X)}")
print(f"   Classes distribution:")
for i, class_name in enumerate(CLASS_NAMES):
    count = np.sum(y == i)
    percentage = (count / len(y)) * 100
    print(f"      {class_name}: {count} ({percentage:.1f}%)")

# Normalize pixel values to [0, 1]
X = X / 255.0

# =====================================
# STEP 2: TRAIN-TEST SPLIT
# =====================================
print("\n🔀 Step 2: Splitting Data...")
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
)

print(f"   Training set: {len(X_train)} images")
print(f"   Validation set: {len(X_val)} images")
print(f"   Test set: {len(X_test)} images")

# =====================================
# STEP 3: COMPUTE CLASS WEIGHTS
# =====================================
print("\n⚖️ Step 3: Computing Class Weights...")
class_weights_array = compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weights = {i: weight for i, weight in enumerate(class_weights_array)}
print(f"   Class weights (to handle imbalance):")
for i, class_name in enumerate(CLASS_NAMES):
    print(f"      {class_name}: {class_weights[i]:.2f}")

# =====================================
# STEP 4: ENHANCED DATA AUGMENTATION
# =====================================
print("\n🎨 Step 4: Setting Up Enhanced Data Augmentation...")
print("   Applied transformations:")
print("      • Rotation: ±25 degrees")
print("      • Width/Height shift: ±25%")
print("      • Brightness: 70%-130%")
print("      • Zoom: ±25%")
print("      • Shear: ±15%")
print("      • Horizontal flip")

train_datagen = ImageDataGenerator(
    rotation_range=25,           # Increased rotation
    width_shift_range=0.25,      # Increased shift
    height_shift_range=0.25,     # Increased shift
    brightness_range=[0.7, 1.3], # NEW: Lighting variations
    zoom_range=0.25,             # Increased zoom
    shear_range=0.15,
    horizontal_flip=True,
    fill_mode='nearest'
)

# No augmentation for validation
val_datagen = ImageDataGenerator()

# Create generators
train_generator = train_datagen.flow(
    X_train, y_train,
    batch_size=BATCH_SIZE,
    shuffle=True
)

val_generator = val_datagen.flow(
    X_val, y_val,
    batch_size=BATCH_SIZE,
    shuffle=False
)

# =====================================
# STEP 5: BUILD IMPROVED MODEL
# =====================================
print("\n🏗️ Step 5: Building Model...")

# Load pre-trained ResNet50 (without top layers)
base_model = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(*IMAGE_SIZE, 3)
)

# Freeze base model layers initially
for layer in base_model.layers:
    layer.trainable = False

# Add custom top layers
print("   Architecture:")
print("      • ResNet50 base (frozen)")
print("      • GlobalAveragePooling2D")
print("      • Dense(256, relu)")
print("      • Dropout(0.5)")
print("      • Dense(128, relu)")
print("      • Dropout(0.3)")
print("      • Dense(4, softmax)")

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(4, activation='softmax')  # 4 classes
])

# Compile model
model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print(f"\n📊 Model Summary:")
print(f"   Total parameters: {model.count_params():,}")
print(f"   Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")

# =====================================
# STEP 6: CALLBACKS FOR BETTER TRAINING
# =====================================
print("\n🎯 Step 6: Setting Up Training Callbacks...")

# Early stopping - stop if no improvement
early_stop = EarlyStopping(
    monitor='val_accuracy',
    patience=10,
    restore_best_weights=True,
    verbose=1
)

# Reduce learning rate when stuck
reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=5,
    min_lr=1e-7,
    verbose=1
)

# Save best model
checkpoint = ModelCheckpoint(
    'models/resnet50/best_model_improved.h5',
    monitor='val_accuracy',
    save_best_only=True,
    verbose=1
)

print("   ✅ Early stopping (patience: 10)")
print("   ✅ Learning rate reduction (factor: 0.5, patience: 5)")
print("   ✅ Best model checkpoint")

# =====================================
# STEP 7: TRAIN MODEL (PHASE 1 - FROZEN)
# =====================================
print("\n🚀 Step 7: Training Model (Phase 1 - Frozen Base)...")
print("   This may take 15-30 minutes depending on your hardware...")

history_phase1 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=20,  # Initial training with frozen base
    class_weight=class_weights,
    callbacks=[early_stop, reduce_lr, checkpoint],
    verbose=1
)

# =====================================
# STEP 8: FINE-TUNING (PHASE 2 - UNFROZEN)
# =====================================
print("\n🔓 Step 8: Fine-tuning (Phase 2 - Unfreeze Base)...")

# Unfreeze last 50 layers of base model
for layer in base_model.layers[-50:]:
    layer.trainable = True

# Recompile with lower learning rate for fine-tuning
model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE / 10),  # 10x lower LR
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print(f"   Unfroze last 50 layers")
print(f"   New learning rate: {LEARNING_RATE / 10}")
print(f"   Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")

history_phase2 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=30,  # Additional fine-tuning epochs
    class_weight=class_weights,
    callbacks=[early_stop, reduce_lr, checkpoint],
    verbose=1
)

# =====================================
# STEP 9: LOAD BEST MODEL & EVALUATE
# =====================================
print("\n📈 Step 9: Loading Best Model and Evaluating...")

# Load best model
best_model = tf.keras.models.load_model('models/resnet50/best_model_improved.h5')

# Evaluate on test set
test_loss, test_acc = best_model.evaluate(X_test, y_test, verbose=0)
print(f"\n✅ Test Accuracy: {test_acc*100:.2f}%")
print(f"   Test Loss: {test_loss:.4f}")

# Get predictions
y_pred_probs = best_model.predict(X_test, verbose=0)
y_pred = np.argmax(y_pred_probs, axis=1)

# =====================================
# STEP 10: DETAILED PER-CLASS ANALYSIS
# =====================================
print("\n📊 Step 10: Per-Class Performance Analysis...")
print("\n" + "="*80)
print("CLASSIFICATION REPORT:")
print("="*80)
print(classification_report(
    y_test, 
    y_pred, 
    target_names=CLASS_NAMES,
    digits=3
))

# Confusion matrix
print("\n" + "="*80)
print("CONFUSION MATRIX:")
print("="*80)
cm = confusion_matrix(y_test, y_pred)
print(f"\nPredicted →")
print(f"Actual ↓     ", end="")
for name in CLASS_NAMES:
    print(f"{name:>8}", end="")
print()
for i, name in enumerate(CLASS_NAMES):
    print(f"{name:>8}:   ", end="")
    for j in range(len(CLASS_NAMES)):
        print(f"{cm[i][j]:>8}", end="")
    print()

# Calculate per-class accuracy
print("\n" + "="*80)
print("PER-CLASS ACCURACY:")
print("="*80)
for i, class_name in enumerate(CLASS_NAMES):
    class_mask = y_test == i
    class_acc = np.mean(y_pred[class_mask] == y_test[class_mask])
    class_count = np.sum(class_mask)
    print(f"   {class_name:>5}: {class_acc*100:>6.2f}%  ({class_count} images)")
    
    # Show which class it's confused with
    if class_acc < 0.9:
        wrong_preds = y_pred[class_mask & (y_pred != y_test)]
        if len(wrong_preds) > 0:
            most_confused = np.bincount(wrong_preds).argmax()
            print(f"         ⚠️  Often confused with: {CLASS_NAMES[most_confused]}")

# =====================================
# STEP 11: TEST SPECIFIC PROBLEM IMAGES
# =====================================
print("\n🔬 Step 11: Testing Previously Problematic Images...")

problem_images = [
    ('25_percent', 36, 25),  # User's problem image
    ('25_percent', 37, 25),
    ('25_percent', 38, 25),
    ('50_percent', 30, 50),
    ('50_percent', 31, 50),
]

print("\nTesting images that had low accuracy before:")
for folder, img_num, expected_class in problem_images:
    img_path = f'{DATA_DIR}/{folder}/{folder}_{img_num}.jpg'
    if os.path.exists(img_path):
        img = tf.keras.preprocessing.image.load_img(img_path, target_size=IMAGE_SIZE)
        img_array = tf.keras.preprocessing.image.img_to_array(img) / 255.0
        img_batch = np.expand_dims(img_array, axis=0)
        
        pred_probs = best_model.predict(img_batch, verbose=0)[0]
        pred_class = np.argmax(pred_probs)
        confidence = pred_probs[pred_class] * 100
        
        expected_idx = [0, 25, 50, 100].index(expected_class)
        status = "✅" if pred_class == expected_idx else "❌"
        
        print(f"   {status} {folder}_{img_num}.jpg:")
        print(f"      Expected: {expected_class}% | Predicted: {CLASS_NAMES[pred_class]} ({confidence:.1f}%)")

# =====================================
# STEP 12: SAVE MODEL METADATA
# =====================================
print("\n💾 Step 12: Saving Model...")

# Save the improved model
best_model.save('models/resnet50/best_model_improved.h5')
print("   ✅ Saved: models/resnet50/best_model_improved.h5")

# Save metadata
metadata = {
    'model_type': 'ResNet50 (Improved)',
    'image_size': IMAGE_SIZE,
    'classes': CLASS_NAMES,
    'test_accuracy': float(test_acc),
    'test_loss': float(test_loss),
    'training_images': len(X_train),
    'batch_size': BATCH_SIZE,
    'epochs_phase1': len(history_phase1.history['loss']),
    'epochs_phase2': len(history_phase2.history['loss']),
    'improvements': [
        'Enhanced data augmentation (brightness, contrast)',
        'Class weights for imbalanced data',
        'Two-phase training (frozen + fine-tuning)',
        'Learning rate scheduling',
        'Early stopping with best model restoration'
    ]
}

import json
with open('models/resnet50/best_model_improved_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
print("   ✅ Saved: models/resnet50/best_model_improved_metadata.json")

# =====================================
# STEP 13: GENERATE COMPARISON REPORT
# =====================================
print("\n📋 Step 13: Generating Comparison Report...")

# Create comparison plot
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Training accuracy
ax1 = axes[0, 0]
ax1.plot(history_phase1.history['accuracy'], label='Phase 1 Train', color='blue', alpha=0.6)
ax1.plot(history_phase1.history['val_accuracy'], label='Phase 1 Val', color='blue', linestyle='--')
phase1_epochs = len(history_phase1.history['accuracy'])
ax1.plot(range(phase1_epochs, phase1_epochs + len(history_phase2.history['accuracy'])), 
         history_phase2.history['accuracy'], label='Phase 2 Train', color='red', alpha=0.6)
ax1.plot(range(phase1_epochs, phase1_epochs + len(history_phase2.history['val_accuracy'])), 
         history_phase2.history['val_accuracy'], label='Phase 2 Val', color='red', linestyle='--')
ax1.axvline(x=phase1_epochs, color='gray', linestyle=':', label='Fine-tuning starts')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy')
ax1.set_title('Training Progress')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Training loss
ax2 = axes[0, 1]
ax2.plot(history_phase1.history['loss'], label='Phase 1 Train', color='blue', alpha=0.6)
ax2.plot(history_phase1.history['val_loss'], label='Phase 1 Val', color='blue', linestyle='--')
ax2.plot(range(phase1_epochs, phase1_epochs + len(history_phase2.history['loss'])), 
         history_phase2.history['loss'], label='Phase 2 Train', color='red', alpha=0.6)
ax2.plot(range(phase1_epochs, phase1_epochs + len(history_phase2.history['val_loss'])), 
         history_phase2.history['val_loss'], label='Phase 2 Val', color='red', linestyle='--')
ax2.axvline(x=phase1_epochs, color='gray', linestyle=':', label='Fine-tuning starts')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Loss')
ax2.set_title('Training Loss')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Confusion matrix heatmap
ax3 = axes[1, 0]
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES, ax=ax3)
ax3.set_xlabel('Predicted')
ax3.set_ylabel('Actual')
ax3.set_title('Confusion Matrix')

# Per-class accuracy bar chart
ax4 = axes[1, 1]
per_class_acc = []
for i in range(len(CLASS_NAMES)):
    class_mask = y_test == i
    class_acc = np.mean(y_pred[class_mask] == y_test[class_mask])
    per_class_acc.append(class_acc * 100)

colors = ['green' if acc >= 80 else 'orange' if acc >= 60 else 'red' for acc in per_class_acc]
bars = ax4.bar(CLASS_NAMES, per_class_acc, color=colors, alpha=0.7)
ax4.axhline(y=80, color='green', linestyle='--', alpha=0.5, label='Target: 80%')
ax4.set_ylabel('Accuracy (%)')
ax4.set_title('Per-Class Accuracy')
ax4.set_ylim([0, 105])
for bar, acc in zip(bars, per_class_acc):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
            f'{acc:.1f}%', ha='center', va='bottom')
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('models/resnet50/training_results_improved.png', dpi=150, bbox_inches='tight')
print("   ✅ Saved: models/resnet50/training_results_improved.png")

# =====================================
# FINAL SUMMARY
# =====================================
print("\n" + "="*80)
print("✅ RETRAINING COMPLETE!")
print("="*80)
print(f"\n📊 Final Results:")
print(f"   Overall Test Accuracy: {test_acc*100:.2f}%")
print(f"\n   Per-Class Results:")
for i, (class_name, acc) in enumerate(zip(CLASS_NAMES, per_class_acc)):
    status = "✅" if acc >= 80 else "⚠️" if acc >= 60 else "❌"
    print(f"      {status} {class_name:>5}: {acc:>6.2f}%")

print(f"\n💡 Next Steps:")
print(f"   1. Review training_results_improved.png for insights")
print(f"   2. If accuracy is good (>80% for 25% and 50%):")
print(f"      - Replace models/resnet50/best_model.h5 with best_model_improved.h5")
print(f"      - Restart your ML service")
print(f"   3. If accuracy still needs improvement:")
print(f"      - Collect more diverse training images")
print(f"      - Try different augmentation parameters")
print(f"      - Consider ensemble methods")

print("\n" + "="*80)
