# Thesis Baseline Comparison Summary

## Classification (Feed Image)
- Best model by F1Score: ResNet50 (F1=0.7961, Accuracy=0.8100)
- Inputs: custom_cnn_metrics.json and resnet50_metrics.json

## Regression (Chickweight Baseline)
- Best model by R2: Linear Regression (R2=0.7436, RMSE=36.13)
- Input: chickweight_model_metrics.json

## Notes
- Feed regression consistency check chart is included because two existing files report different R2 values.
- If you add MobileNetV2 metrics later, extend this script to include that baseline in the same charts.

## Generated Outputs
- Graphs: D:\Research\data_anaysis\results\visualizations\thesis_baseline
- Tables: D:\Research\data_anaysis\results\metrics\thesis_baseline