"""
Helper Functions for Poultry Feed Classification Project
Reusable utility functions for data loading, preprocessing, and evaluation
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import cv2
import json
from datetime import datetime
from sklearn.metrics import classification_report, confusion_matrix


def count_images(data_path, classes):
    """Count images in each class folder"""
    image_counts = {}
    for class_name in classes:
        class_path = os.path.join(data_path, class_name)
        if os.path.exists(class_path):
            images = [f for f in os.listdir(class_path) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
            image_counts[class_name] = len(images)
        else:
            image_counts[class_name] = 0
    return image_counts


def load_dataset(data_path, classes, img_size):
    """Load and preprocess all images from dataset folders"""
    images = []
    labels = []
    
    for class_idx, class_name in enumerate(classes):
        class_path = os.path.join(data_path, class_name)
        print(f"Loading images from {class_name}...")
        
        if os.path.exists(class_path):
            image_files = [f for f in os.listdir(class_path) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
            
            for img_file in image_files:
                img_path = os.path.join(class_path, img_file)
                try:
                    img = cv2.imread(img_path)
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, img_size)
                        img = img / 255.0  # Normalize to [0, 1]
                        images.append(img)
                        labels.append(class_idx)
                except Exception as e:
                    print(f"Error loading {img_path}: {e}")
        else:
            print(f"Warning: {class_path} does not exist!")
    
    return np.array(images), np.array(labels)


def plot_class_distribution(image_counts, title="Class Distribution"):
    """Visualize image distribution across classes"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Bar plot
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    ax1.bar(image_counts.keys(), image_counts.values(), color=colors)
    ax1.set_xlabel('Class', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Images', fontsize=12, fontweight='bold')
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', alpha=0.3)
    
    # Pie chart
    ax2.pie(image_counts.values(), labels=image_counts.keys(), 
            autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title('Distribution (%)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_sample_images(data_path, classes, samples_per_class=5):
    """Display sample images from each class"""
    fig, axes = plt.subplots(len(classes), samples_per_class, 
                            figsize=(15, len(classes)*3))
    fig.suptitle('Sample Images from Each Class', fontsize=16, fontweight='bold')
    
    for idx, class_name in enumerate(classes):
        class_path = os.path.join(data_path, class_name)
        if os.path.exists(class_path):
            images = [f for f in os.listdir(class_path) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
            
            for i in range(min(samples_per_class, len(images))):
                img_path = os.path.join(class_path, images[i])
                img = cv2.imread(img_path)
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    axes[idx, i].imshow(img)
                    axes[idx, i].axis('off')
                    if i == 0:
                        axes[idx, i].set_title(f'{class_name}', 
                                              fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_confusion_matrix(y_true, y_pred, classes, title="Confusion Matrix"):
    """Plot confusion matrix heatmap"""
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=classes, yticklabels=classes,
                cbar_kws={'label': 'Count'}, linewidths=1, linecolor='gray')
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('True Label', fontsize=12, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=12, fontweight='bold')
    plt.tight_layout()
    return plt.gcf()


def save_metrics(model_name, metrics_dict, save_dir='results/metrics'):
    """Save model metrics to JSON file"""
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{model_name}_metrics_{timestamp}.json"
    filepath = os.path.join(save_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(metrics_dict, f, indent=4)
    
    print(f"Metrics saved to: {filepath}")
    return filepath


def save_training_history(model_name, history, save_dir='results/metrics'):
    """Save training history to CSV"""
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{model_name}_history_{timestamp}.csv"
    filepath = os.path.join(save_dir, filename)
    
    df = pd.DataFrame(history.history)
    df.to_csv(filepath, index=False)
    
    print(f"Training history saved to: {filepath}")
    return filepath


def plot_training_history(history, model_name="Model"):
    """Plot training history (accuracy and loss)"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Accuracy
    axes[0].plot(history.history['accuracy'], label='Training', linewidth=2)
    axes[0].plot(history.history['val_accuracy'], label='Validation', linewidth=2)
    axes[0].set_title(f'{model_name} - Accuracy', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Accuracy', fontsize=12)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Loss
    axes[1].plot(history.history['loss'], label='Training', linewidth=2)
    axes[1].plot(history.history['val_loss'], label='Validation', linewidth=2)
    axes[1].set_title(f'{model_name} - Loss', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Loss', fontsize=12)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def compare_models(models_results):
    """
    Compare multiple models performance
    
    Args:
        models_results: dict with model names as keys and metrics dict as values
        Example: {'Custom CNN': {'accuracy': 0.95, 'precision': 0.94, ...}, ...}
    """
    metrics_df = pd.DataFrame(models_results).T
    
    # Plot comparison
    fig, ax = plt.subplots(figsize=(12, 6))
    metrics_df[['accuracy', 'precision', 'recall', 'f1_score']].plot(
        kind='bar', ax=ax, rot=0, width=0.8
    )
    ax.set_title('Model Performance Comparison', fontsize=16, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_xlabel('Model', fontsize=12, fontweight='bold')
    ax.legend(['Accuracy', 'Precision', 'Recall', 'F1-Score'], fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim([0, 1.1])
    
    plt.tight_layout()
    return fig, metrics_df


def print_model_summary(model_name, metrics):
    """Print formatted model performance summary"""
    print("=" * 70)
    print(f"{model_name.upper()} - PERFORMANCE SUMMARY")
    print("=" * 70)
    print(f"Accuracy:        {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"Precision:       {metrics['precision']:.4f}")
    print(f"Recall:          {metrics['recall']:.4f}")
    print(f"F1-Score:        {metrics['f1_score']:.4f}")
    if 'training_time' in metrics:
        print(f"Training Time:   {metrics['training_time']:.2f} seconds")
    if 'parameters' in metrics:
        print(f"Parameters:      {metrics['parameters']:,}")
    print("=" * 70)
