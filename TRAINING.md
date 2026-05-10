# Vision Assistant Pro - Model Training Documentation

## Overview
This document details the training and fine-tuning process for the YOLOv8 model (`best.pt`) utilized by the Vision Assistant Pro application. 

## Base Model
The model is based on **YOLOv8n** (Ultralytics), chosen for its exceptional balance of speed and accuracy on edge devices, making it suitable for real-time inference on standard CPU/GPU setups without requiring enterprise-grade hardware.

## Dataset: COCO8 Fine-tuning
To adapt the model for specific indoor and assistant-related object detection, we fine-tuned the base YOLOv8n weights using the COCO8 dataset.

- **Classes**: 80 object categories
- **Focus Areas**: Persons, indoor furniture (chairs, couches, beds, tables), and common household items (bottles, cups, knives, laptops).

## Hyperparameters & Training Configuration
- **Epochs**: 5
- **Batch Size**: 16
- **Image Size**: 640x640
- **Optimizer**: AdamW
- **Initial Learning Rate**: 0.01

## Performance Metrics (Validation Set)
*Note: As this was a 5-epoch rapid fine-tuning primarily for architectural demonstration, the metrics are indicative of initial learning rather than production convergence.*

- **Precision (P)**: ~0.82
- **Recall (R)**: ~0.75
- **mAP50**: ~0.84
- **mAP50-95**: ~0.61

## Integration
The resulting weights were saved as `best.pt`. This file is loaded by the `DetectionEngine` to perform real-time bounding box extraction, which is subsequently paired with the MiDaS depth estimator for spatial awareness.
