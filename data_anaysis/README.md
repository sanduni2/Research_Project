# Poultry Feed Optimization and Growth Prediction System
## Final Year Research Project - IT Undergraduate

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Project Overview

This research project focuses on developing an intelligent **Poultry Feed Optimization System** using deep learning techniques for automated feed level classification. The system will be integrated into a web application for real-time feed monitoring and growth prediction.

### Research Objectives

1. **Primary Goal**: Develop accurate deep learning models for poultry feed classification
2. **Secondary Goal**: Comparative analysis of different CNN architectures
3. **Application**: Web-based feed optimization and growth prediction system
4. **Target Accuracy**: ≥95% classification accuracy

---

## 📁 Project Structure

```
data_anaysis/
├── data/                          # Dataset folder
│   ├── 0_percent/                # Images with 0% feed level
│   ├── 25_percent/               # Images with 25% feed level
│   ├── 50_percent/               # Images with 50% feed level
│   └── 100_percent/              # Images with 100% feed level
│
├── notebooks/                     # Jupyter notebooks (Research & Analysis)
│   ├── 01_data_exploration.ipynb        # ✓ Exploratory Data Analysis
│   ├── 02_model_custom_cnn.ipynb        # ✓ Custom CNN Architecture
│   ├── 03_model_resnet50.ipynb          # Transfer Learning: ResNet50
│   ├── 04_model_mobilenetv2.ipynb       # Transfer Learning: MobileNetV2
│   └── 05_comparative_analysis.ipynb    # Model Comparison & Selection
│
├── models/                        # Trained model artifacts
│   ├── custom_cnn/               # Custom CNN saved models
│   ├── resnet50/                 # ResNet50 saved models
│   └── mobilenetv2/              # MobileNetV2 saved models
│
├── results/                       # Research results
│   ├── metrics/                  # Performance metrics (CSV, JSON)
│   │   ├── dataset_summary.csv
│   │   ├── model_comparison.csv
│   │   └── *_metrics.json
│   └── visualizations/           # Publication-quality figures
│       ├── fig1_dataset_distribution.png
│       ├── fig2_sample_images.png
│       ├── fig3_image_properties.png
│       ├── fig4_color_analysis.png
│       ├── fig5_*_architecture.png
│       ├── fig6_*_training_history.png
│       ├── fig7_*_confusion_matrix.png
│       └── fig8_*_per_class_metrics.png
│
├── utils/                         # Utility functions
│   └── helper_functions.py       # Reusable data processing functions
│
├── README.md                      # Project documentation (this file)
└── requirements.txt               # Python dependencies
```

---

## 🎯 Research Methodology

### Phase 1: Data Collection & Preparation
- [x] Dataset organization (4 feed level categories)
- [x] Image quality assessment
- [x] Class distribution analysis
- [x] Data preprocessing pipeline

### Phase 2: Model Development & Training

#### Model 1: Custom CNN (Baseline)
- **Architecture**: 3 convolutional blocks (32→64→128 filters)
- **Layers**: Conv2D, BatchNormalization, MaxPooling, Dropout
- **Purpose**: Establish baseline performance
- **Status**: ✓ Implemented

#### Model 2: ResNet50 (Transfer Learning)
- **Base**: Pre-trained on ImageNet
- **Fine-tuning**: Last layers customized for 4-class classification
- **Purpose**: Leverage pre-trained features
- **Expected**: Higher accuracy, faster convergence

#### Model 3: MobileNetV2 (Lightweight)
- **Base**: Efficient architecture for deployment
- **Advantages**: Smaller size, faster inference
- **Purpose**: Optimize for web application deployment
- **Expected**: Good accuracy-to-size ratio

### Phase 3: Comparative Analysis
- Performance metrics comparison
- Statistical significance testing
- Model selection for web deployment
- Error analysis and optimization

---

## 📊 Evaluation Metrics

### Primary Metrics
- **Accuracy**: Overall classification correctness
- **Precision**: Positive prediction accuracy per class
- **Recall**: True positive detection rate
- **F1-Score**: Harmonic mean of precision and recall

### Secondary Metrics
- **Training Time**: Model convergence speed
- **Model Size**: Storage and memory requirements
- **Inference Time**: Prediction speed (for web app)
- **Confusion Matrix**: Error pattern analysis

### Performance Targets
- Minimum Accuracy: 90%
- Target Accuracy: 95%+
- Maximum Inference Time: <100ms
- Model Size: <100MB (for web deployment)

---

## 🚀 Quick Start Guide

### Prerequisites
```bash
Python 3.8+
TensorFlow 2.x
CUDA (optional, for GPU acceleration)
```

### Installation
```bash
# Clone repository
git clone <your-repo-url>
cd data_anaysis

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Execution Workflow

#### Step 1: Data Exploration
```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```
**Outputs**: 
- Dataset statistics
- Figures 1-4 (distribution, samples, properties, color analysis)

#### Step 2: Train Custom CNN
```bash
jupyter notebook notebooks/02_model_custom_cnn.ipynb
```
**Outputs**:
- Trained model (`.h5`)
- Figures 5-8 (architecture, training curves, confusion matrix, metrics)
- Performance metrics (JSON, CSV)

#### Step 3: Train ResNet50 (Transfer Learning)
```bash
jupyter notebook notebooks/03_model_resnet50.ipynb
```

#### Step 4: Train MobileNetV2 (Transfer Learning)
```bash
jupyter notebook notebooks/04_model_mobilenetv2.ipynb
```

#### Step 5: Comparative Analysis
```bash
jupyter notebook notebooks/05_comparative_analysis.ipynb
```
**Outputs**:
- Side-by-side model comparison
- Statistical analysis
- Best model recommendation
- Research paper figures and tables

---

## 📈 Expected Results

### Performance Benchmarks (Estimated)

| Model | Accuracy | Precision | Recall | F1-Score | Parameters | Inference Time |
|-------|----------|-----------|--------|----------|------------|----------------|
| Custom CNN | 90-93% | 0.90-0.93 | 0.89-0.92 | 0.90-0.92 | ~2M | ~50ms |
| ResNet50 | 94-97% | 0.94-0.97 | 0.93-0.96 | 0.94-0.97 | ~25M | ~80ms |
| MobileNetV2 | 92-95% | 0.92-0.95 | 0.91-0.94 | 0.92-0.95 | ~3M | ~40ms |

*Note: Actual results depend on dataset quality and training conditions*

---

## 📦 Dependencies

### Core Libraries
```
tensorflow>=2.10.0
keras>=2.10.0
numpy>=1.23.0
pandas>=1.5.0
matplotlib>=3.6.0
seaborn>=0.12.0
opencv-python>=4.7.0
scikit-learn>=1.2.0
```

### Visualization
```
plotly>=5.11.0
graphviz>=0.20.0  # For model architecture diagrams
```

### Utilities
```
jupyter>=1.0.0
ipykernel>=6.0.0
tqdm>=4.64.0
```

---

## 📝 Research Paper Figures

All figures are generated in **publication-quality** (300 DPI, vector graphics where possible):

1. **Figure 1**: Dataset Distribution Analysis (3 subplots)
2. **Figure 2**: Representative Sample Images (4×6 grid)
3. **Figure 3**: Image Properties Analysis (dimensions, sizes)
4. **Figure 4**: RGB Color Channel Distribution
5. **Figure 5**: Model Architecture Diagrams (per model)
6. **Figure 6**: Training History (accuracy, loss, precision, recall)
7. **Figure 7**: Confusion Matrix (raw counts + normalized)
8. **Figure 8**: Per-Class Performance Metrics
9. **Figure 9**: Model Comparison (comparative analysis)
10. **Figure 10**: ROC Curves (if applicable)

---

## 🔬 Research Contributions

### Novel Aspects
1. Comparative study of CNN architectures for poultry feed classification
2. Custom data augmentation strategies for agricultural imaging
3. Real-world deployment considerations (model size vs. accuracy trade-off)
4. Integration pathway for web-based monitoring systems

### Practical Applications
- **Feed Optimization**: Automated monitoring of feed levels
- **Cost Reduction**: Minimize feed waste
- **Growth Prediction**: Correlate feed levels with growth rates
- **Farm Management**: Web-based dashboard for poultry farms

---

## 🌐 Web Application Integration

### Planned Features
1. **Real-time Feed Monitoring**: Upload images for instant classification
2. **Historical Tracking**: Feed level trends over time
3. **Growth Prediction**: ML-based forecasting
4. **Alert System**: Notifications for low feed levels
5. **Analytics Dashboard**: Visualization of feed patterns

### Technology Stack (Proposed)
- **Backend**: Flask/FastAPI (Python)
- **Frontend**: React.js
- **Database**: PostgreSQL
- **ML Deployment**: TensorFlow.js or TF Serving
- **Cloud**: AWS/Azure (deployment ready)

---

## 👨‍🎓 Author Information

**Final Year Research Project**  
**Program**: Bachelor of IT  
**Focus**: Machine Learning & Computer Vision  
**Year**: 2025/2026

---

## 📄 Citation

If you use this work in your research, please cite:

```bibtex
@thesis{poultry_feed_optimization_2026,
  title={Poultry Feed Optimization and Growth Prediction Using Deep Learning},
  author={[Your Name]},
  year={2026},
  school={[Your University]},
  type={Final Year Project}
}
```

---

## 📧 Contact & Support

For questions or collaborations:
- **Email**: [your.email@university.edu]
- **GitHub**: [your-github-profile]
- **LinkedIn**: [your-linkedin-profile]

---

## 🙏 Acknowledgments

- Supervisor: [Supervisor Name]
- Dataset: [Dataset Source/Contributors]
- Libraries: TensorFlow, Keras, scikit-learn teams
- Community: Stack Overflow, GitHub, Kaggle

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

**Last Updated**: January 1, 2026  
**Status**: ✓ Data Analysis Complete | ⏳ Model Training In Progress  
**Version**: 1.0.0
