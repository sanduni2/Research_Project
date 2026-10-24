"""
MEMORY-EFFICIENT FEED CONSUMPTION MODEL RETRAINING
Uses Keras data generators to avoid loading all images into RAM

Improvements:
- Memory-efficient data loading (loads batches on-the-fly)
- Enhanced data augmentation (brightness, contrast, lighting variations)
- Class weights to focus on 25% and 50% classes
- Two-phase training (freeze → fine-tune)
- Detailed per-class evaluation
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import seaborn as sns

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

print("="*80)
print("🔄 RETRAINING FEED CONSUMPTION MODEL - Memory-Efficient Version")
print("="*80)

# =====================================
# CONFIGURATION
# =====================================
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS_PHASE1 = 20  # Frozen base
EPOCHS_PHASE2 = 30  # Fine-tuning
LEARNING_RATE = 0.0001
DATA_DIR = 'data'
MODEL_SAVE_PATH = 'models/resnet50/best_model_improved.h5'

print(f"\n⚙️ Configuration:")
print(f"   Image Size: {IMAGE_SIZE}")
print(f"   Batch Size: {BATCH_SIZE}")
print(f"   Phase 1 Epochs (Frozen): {EPOCHS_PHASE1}")
print(f"   Phase 2 Epochs (Fine-tune): {EPOCHS_PHASE2}")
print(f"   Learning Rate: {LEARNING_RATE}")

# =====================================
# STEP 1: SETUP DATA GENERATORS
# =====================================
print("\n📂 Step 1: Setting up Data Generators...")

# Enhanced data augmentation - KEY FOR FEED IMAGES!
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    width_shift_range=0.25,
    height_shift_range=0.25,
    brightness_range=[0.7, 1.3],  # Critical for lighting variations!
    zoom_range=0.25,
    shear_range=0.15,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2  # 80% train, 20% validation
)

# Validation data - only rescaling, no augmentation
val_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

# Training generator
train_generator = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='sparse',  # For integer labels (0, 1, 2, 3)
    subset='training',
    shuffle=True
)

# Validation generator
validation_generator = val_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='sparse',
    subset='validation',
    shuffle=False
)

print(f"\n✅ Data loaded:")
print(f"   Training samples: {train_generator.samples}")
print(f"   Validation samples: {validation_generator.samples}")
print(f"   Classes: {train_generator.class_indices}")

# =====================================
# STEP 2: COMPUTE CLASS WEIGHTS
# =====================================
print("\n⚖️ Step 2: Computing Class Weights...")

# Count samples per class
class_counts = {}
for class_name, class_idx in train_generator.class_indices.items():
    class_folder = os.path.join(DATA_DIR, class_name)
    if os.path.exists(class_folder):
        count = len([f for f in os.listdir(class_folder) if f.endswith(('.jpg', '.jpeg', '.png'))])
        class_counts[class_idx] = count

# Calculate weights (focus more on 25% and 50%)
class_weights = {}
for idx in range(len(class_counts)):
    if idx in [1, 2]:  # 25% and 50% classes
        class_weights[idx] = 1.5  # 50% more weight
    else:
        class_weights[idx] = 1.0

print(f"   Class weights: {class_weights}")
print(f"   (25% and 50% classes get 1.5x weight)")

# =====================================
# STEP 3: BUILD MODEL
# =====================================
print("\n🏗️ Step 3: Building ResNet50 Model...")

# Load pre-trained ResNet50
base_model = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(*IMAGE_SIZE, 3)
)

# Freeze base model initially
base_model.trainable = False

# Add custom classification head
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.3)(x)
predictions = Dense(4, activation='softmax')(x)  # 4 classes

model = Model(inputs=base_model.input, outputs=predictions)

# Compile model
model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print(f"✅ Model built with {model.count_params():,} parameters")
print(f"   ResNet50 base: Frozen")

# =====================================
# STEP 4: PHASE 1 TRAINING (FROZEN BASE)
# =====================================
print("\n🎯 Step 4: Phase 1 Training (Frozen Base)...")
print(f"   Training for {EPOCHS_PHASE1} epochs...")

# Callbacks
callbacks_phase1 = [
    EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1
    ),
    ModelCheckpoint(
        'models/resnet50/checkpoint_phase1.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=0
    )
]

history_phase1 = model.fit(
    train_generator,
    epochs=EPOCHS_PHASE1,
    validation_data=validation_generator,
    class_weight=class_weights,
    callbacks=callbacks_phase1,
    verbose=1
)

print("✅ Phase 1 completed!")

# =====================================
# STEP 5: PHASE 2 TRAINING (FINE-TUNING)
# =====================================
print("\n🔥 Step 5: Phase 2 Training (Fine-tuning)...")

# Unfreeze last 50 layers of ResNet50
base_model.trainable = True
for layer in base_model.layers[:-50]:
    layer.trainable = False

print(f"   Unfrozen last 50 layers of ResNet50")

# Re-compile with lower learning rate
model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE / 10),  # 10x lower LR for fine-tuning
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Callbacks for phase 2
callbacks_phase2 = [
    EarlyStopping(
        monitor='val_loss',
        patience=8,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=4,
        min_lr=1e-8,
        verbose=1
    ),
    ModelCheckpoint(
        MODEL_SAVE_PATH,
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
]

print(f"   Training for {EPOCHS_PHASE2} epochs...")

history_phase2 = model.fit(
    train_generator,
    epochs=EPOCHS_PHASE2,
    validation_data=validation_generator,
    class_weight=class_weights,
    callbacks=callbacks_phase2,
    verbose=1
)

print("✅ Phase 2 completed!")

# =====================================
# STEP 6: EVALUATE MODEL
# =====================================
print("\n📊 Step 6: Evaluating Model...")

# Load best model
model.load_weights(MODEL_SAVE_PATH)

# Predictions on validation set
validation_generator.reset()
y_pred_probs = model.predict(validation_generator, verbose=1)
y_pred = np.argmax(y_pred_probs, axis=1)
y_true = validation_generator.classes

# Overall accuracy
accuracy = accuracy_score(y_true, y_pred)
print(f"\n✅ Overall Validation Accuracy: {accuracy*100:.2f}%")

# Per-class metrics
print("\n📈 Per-Class Performance:")
class_labels = ['0%', '25%', '50%', '100%']
report = classification_report(y_true, y_pred, target_names=class_labels, output_dict=True)

for class_name in class_labels:
    metrics = report[class_name]
    print(f"\n   {class_name} Class:")
    print(f"      Precision: {metrics['precision']*100:.1f}%")
    print(f"      Recall: {metrics['recall']*100:.1f}%")
    print(f"      F1-Score: {metrics['f1-score']*100:.1f}%")
    print(f"      Support: {int(metrics['support'])} samples")

# =====================================
# STEP 7: SAVE RESULTS
# =====================================
print("\n💾 Step 7: Saving Results...")

# Plot training history
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

# Combine both phases
all_loss = history_phase1.history['loss'] + history_phase2.history['loss']
all_val_loss = history_phase1.history['val_loss'] + history_phase2.history['val_loss']
all_accuracy = history_phase1.history['accuracy'] + history_phase2.history['accuracy']
all_val_accuracy = history_phase1.history['val_accuracy'] + history_phase2.history['val_accuracy']

# Loss plot
ax1.plot(all_loss, label='Training Loss', linewidth=2)
ax1.plot(all_val_loss, label='Validation Loss', linewidth=2)
ax1.axvline(x=EPOCHS_PHASE1, color='red', linestyle='--', label='Phase 2 Start')
ax1.set_title('Model Loss', fontsize=14, fontweight='bold')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Accuracy plot
ax2.plot([a*100 for a in all_accuracy], label='Training Accuracy', linewidth=2)
ax2.plot([a*100 for a in all_val_accuracy], label='Validation Accuracy', linewidth=2)
ax2.axvline(x=EPOCHS_PHASE1, color='red', linestyle='--', label='Phase 2 Start')
ax2.set_title('Model Accuracy', fontsize=14, fontweight='bold')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Accuracy (%)')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('training_results_improved.png', dpi=300, bbox_inches='tight')
print("   ✅ Training curves saved: training_results_improved.png")

# Confusion matrix
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=class_labels, yticklabels=class_labels,
            cbar_kws={'label': 'Count'})
plt.title('Confusion Matrix - Improved Model', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('True Label', fontsize=12)
plt.xlabel('Predicted Label', fontsize=12)
plt.tight_layout()
plt.savefig('confusion_matrix_improved.png', dpi=300, bbox_inches='tight')
print("   ✅ Confusion matrix saved: confusion_matrix_improved.png")

# Save detailed report
with open('training_report_improved.txt', 'w') as f:
    f.write("="*80 + "\n")
    f.write("IMPROVED FEED CONSUMPTION MODEL - TRAINING REPORT\n")
    f.write("="*80 + "\n\n")
    f.write(f"Overall Validation Accuracy: {accuracy*100:.2f}%\n\n")
    f.write("Per-Class Performance:\n")
    f.write("-"*80 + "\n")
    for class_name in class_labels:
        metrics = report[class_name]
        f.write(f"\n{class_name} Class:\n")
        f.write(f"  Precision: {metrics['precision']*100:.1f}%\n")
        f.write(f"  Recall: {metrics['recall']*100:.1f}%\n")
        f.write(f"  F1-Score: {metrics['f1-score']*100:.1f}%\n")
        f.write(f"  Support: {int(metrics['support'])} samples\n")

print("   ✅ Detailed report saved: training_report_improved.txt")

print("\n" + "="*80)
print("✅ RETRAINING COMPLETED SUCCESSFULLY!")
print("="*80)
print(f"\n📦 Model saved: {MODEL_SAVE_PATH}")
print(f"📊 Overall Accuracy: {accuracy*100:.2f}%")
print("\n💡 Next steps:")
print("   1. Run deploy_improved_model.py to deploy the new model")
print("   2. Restart ML service to load the updated model")
print("   3. Test with problematic images (25%, 50% classes)")
