# 🌿 Plant Disease Classification Model (ResNet50)

A deep learning model for classifying plant diseases using Transfer
Learning with ResNet50. This model identifies 38 different plant disease
conditions across multiple crops.

------------------------------------------------------------------------

## 🎯 Overview

This project implements a plant disease classification system capable of
identifying 38 plant health conditions using a pretrained ResNet50
model.

### Crops Covered:

Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato,
Raspberry, Soybean, Squash, Strawberry, Tomato

### Conditions:

Includes multiple diseases (bacterial spot, blight, rust, mildew, virus
infections) and healthy classes.

------------------------------------------------------------------------

## 📊 Dataset

-   Total Images: 54,284
-   Number of Classes: 38
-   Image Size: 224×224
-   Training: 34,741
-   Validation: 8,686
-   Test: 10,857

------------------------------------------------------------------------

## 🏗️ Model Architecture

Base Model: ResNet50 (ImageNet Pretrained)

Input (224x224x3) ↓ ResNet50 (Frozen) ↓ GlobalAveragePooling2D ↓
BatchNormalization ↓ Dropout (0.5) ↓ Dense (256, ReLU) ↓ Dropout (0.3) ↓
Dense (38, Softmax)

------------------------------------------------------------------------

## ⚙️ Requirements

Python 3.8+ tensorflow\>=2.10.0 keras\>=2.10.0 numpy pandas matplotlib
seaborn scikit-learn Pillow

------------------------------------------------------------------------

## 🚀 Installation

1.  Clone repository git clone `<your-repo-url>`{=html}

2.  Install dependencies pip install -r requirements.txt

3.  Organize dataset plant_dataset/ ├── Apple\_**Apple_scab/ ├──
    Apple**\_Black_rot/ └── ...

------------------------------------------------------------------------

## 📖 Training

-   Freeze ResNet50 base model
-   Train for 25--30 epochs
-   Use Adam optimizer
-   Loss: Categorical Crossentropy
-   Learning Rate: 0.0001

------------------------------------------------------------------------

## 📈 Model Performance

Validation Accuracy: \~96--97% Batch Size: 32 Epochs: 25

------------------------------------------------------------------------

## 📱 Deployment

Model converted to TensorFlow Lite.

Input: Shape: (1, 224, 224, 3) Type: float32 Preprocessing:
preprocess_input()

Output: Shape: (1, 38) Softmax probability distribution

------------------------------------------------------------------------

## ⚠️ Limitations

-   Larger size compared to MobileNetV2
-   Slower inference on low-end devices
-   Requires proper preprocessing

------------------------------------------------------------------------

## 🔮 Future Improvements

-   Fine-tuning top layers
-   Quantization (INT8)
-   Grad-CAM visualization
-   Advanced data augmentation

------------------------------------------------------------------------

## 📄 License

MIT License

------------------------------------------------------------------------

Last Updated: February 2026 Model Version: 1.0 Framework: TensorFlow 2.x
