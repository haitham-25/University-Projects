# Plant Disease Classification Model 🌿

A deep learning model for classifying plant diseases using transfer learning with MobileNetV2. This model can identify 38 different plant disease conditions across multiple crop types.

## 📋 Table of Contents
- [Overview](#overview)
- [Dataset](#dataset)
- [Model Architecture](#model-architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Model Performance](#model-performance)
- [Files Description](#files-description)
- [Deployment](#deployment)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [License](#license)

## 🎯 Overview

This project implements a plant disease classification system capable of identifying 38 different classes of plant health conditions including:
- **Crops covered**: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato
- **Conditions**: Various diseases (bacterial spot, blight, rust, mildew, etc.) and healthy plants

The model uses **MobileNetV2** as a base architecture with transfer learning, making it lightweight and suitable for mobile deployment.

## 📊 Dataset

- **Total Images**: 54,284
- **Number of Classes**: 38
- **Image Size**: 224×224 pixels
- **Data Split**:
  - Training: 34,741 images (64%)
  - Validation: 8,686 images (16%)
  - Test: 10,857 images (20%)

### Supported Classes:
```
1. Apple___Apple_scab
2. Apple___Black_rot
3. Apple___Cedar_apple_rust
4. Apple___healthy
5. Blueberry___healthy
6. Cherry_(including_sour)___Powdery_mildew
7. Cherry_(including_sour)___healthy
8. Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot
9. Corn_(maize)___Common_rust_
10. Corn_(maize)___Northern_Leaf_Blight
11. Corn_(maize)___healthy
12. Grape___Black_rot
13. Grape___Esca_(Black_Measles)
14. Grape___Leaf_blight_(Isariopsis_Leaf_Spot)
15. Grape___healthy
16. Orange___Haunglongbing_(Citrus_greening)
17. Peach___Bacterial_spot
18. Peach___healthy
19. Pepper,_bell___Bacterial_spot
20. Pepper,_bell___healthy
21. Potato___Early_blight
22. Potato___Late_blight
23. Potato___healthy
24. Raspberry___healthy
25. Soybean___healthy
26. Squash___Powdery_mildew
27. Strawberry___Leaf_scorch
28. Strawberry___healthy
29. Tomato___Bacterial_spot
30. Tomato___Early_blight
31. Tomato___Late_blight
32. Tomato___Leaf_Mold
33. Tomato___Septoria_leaf_spot
34. Tomato___Spider_mites Two-spotted_spider_mite
35. Tomato___Target_Spot
36. Tomato___Tomato_Yellow_Leaf_Curl_Virus
37. Tomato___Tomato_mosaic_virus
38. Tomato___healthy
```

## 🏗️ Model Architecture

**Base Model**: MobileNetV2 (pretrained on ImageNet)

```
Input (224×224×3)
    ↓
MobileNetV2 Base (frozen)
    ↓
GlobalAveragePooling2D
    ↓
Dropout (0.3)
    ↓
Dense (38, softmax)
    ↓
Output (38 classes)
```

### Key Features:
- **Transfer Learning**: Leverages ImageNet pretrained weights
- **Frozen Base**: MobileNetV2 weights are frozen to prevent overfitting
- **GlobalAveragePooling2D**: Reduces parameters compared to Flatten
- **Dropout**: 30% dropout for regularization
- **Optimizer**: Adam
- **Loss Function**: Categorical Crossentropy

## 💻 Requirements

```
Python 3.7+
tensorflow>=2.8.0
keras>=2.8.0
numpy>=1.19.0
pandas>=1.2.0
scikit-learn>=0.24.0
scikit-image>=0.18.0
matplotlib>=3.3.0
seaborn>=0.11.0
Pillow>=8.0.0
```

## 🚀 Installation

1. **Clone or download the repository**
```bash
git clone <your-repo-url>
cd plant-disease-classification
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Organize your dataset**
```
plant_dataset/
├── Apple___Apple_scab/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── Apple___Black_rot/
│   └── ...
└── ...
```

## 📖 Usage

### Training the Model

1. **Update the data path in the notebook**
```python
data = r'path/to/your/plant_dataset'
```

2. **Run the notebook cells sequentially**
   - Data preprocessing and augmentation
   - Model building
   - Training (25 epochs)
   - Model evaluation

### Making Predictions

**Using the saved Keras model (.h5):**
```python
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

# Load model
model = tf.keras.models.load_model('best_plant_model.h5')

# Load and preprocess image
img = load_img('path/to/image.jpg', target_size=(224, 224))
img_array = img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array = img_array / 255.0

# Predict
predictions = model.predict(img_array)
predicted_class = np.argmax(predictions)
confidence = np.max(predictions)

print(f"Predicted class: {predicted_class}")
print(f"Confidence: {confidence:.2%}")
```

**Using TensorFlow Lite (.tflite):**
```python
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load and preprocess image
img = load_img('path/to/image.jpg', target_size=(224, 224))
img_array = img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array = img_array / 255.0

# Run inference
interpreter.set_tensor(input_details[0]['index'], img_array.astype(np.float32))
interpreter.invoke()

# Get results
output_data = interpreter.get_tensor(output_details[0]['index'])
predicted_class = np.argmax(output_data)
confidence = np.max(output_data)

print(f"Predicted class: {predicted_class}")
print(f"Confidence: {confidence:.2%}")
```

## 📈 Model Performance

- **Validation Accuracy**: ~94%
- **Training Epochs**: 25
- **Best Model Saved**: Epoch 10 (val_accuracy: 0.9414)
- **Batch Size**: 32
- **Learning Rate**: 0.001

### Training History:
- Epoch 1: 79.5% train acc, 89.8% val acc
- Epoch 5: 89.8% train acc, 93.5% val acc
- Epoch 7: 90.2% train acc, 94.0% val acc
- Epoch 10: ~90.5% train acc, 94.1% val acc

## 📁 Files Description

| File | Description |
|------|-------------|
| `mobv2.ipynb` | Main Jupyter notebook with complete pipeline |
| `best_plant_model.h5` | Trained Keras model (saved at best validation accuracy) |
| `model.tflite` | TensorFlow Lite converted model for mobile deployment |
| `README.md` | This file |

## 📱 Deployment

The model has been converted to TensorFlow Lite format for deployment on:
- Mobile applications (Android/iOS)
- Edge devices
- Embedded systems
- IoT devices

**Model Size**: ~9.7 MB (H5 format)

**Input Specifications**:
- Shape: (1, 224, 224, 3)
- Type: float32
- Range: [0, 1]

**Output Specifications**:
- Shape: (1, 38)
- Type: float32
- Format: Probability distribution over 38 classes

## ⚠️ Limitations

1. **Preprocessing**: Currently uses simple rescaling (1./255) instead of MobileNetV2's standard preprocessing function
2. **No Fine-tuning**: Base MobileNetV2 layers remain frozen; unfreezing top layers could improve accuracy
3. **Class Imbalance**: Some classes may have fewer samples than others
4. **Limited Augmentation**: Only basic augmentation techniques applied
5. **Single Crop Focus**: Model trained on specific crop types; may not generalize to other plants

## 🔮 Future Improvements

1. **Use MobileNetV2 Preprocessing**:
```python
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
train_datagen = ImageDataGenerator(preprocessing_function=preprocess_input, ...)
```

2. **Implement Fine-tuning**:
   - Unfreeze top 30 layers of MobileNetV2
   - Train with lower learning rate (1e-5)
   - Expected accuracy gain: 2-3%

3. **Add Callbacks**:
   - EarlyStopping
   - ReduceLROnPlateau
   - TensorBoard logging

4. **Advanced Augmentation**:
   - Mixup
   - CutMix
   - AutoAugment

5. **Ensemble Methods**:
   - Combine multiple models
   - Test-time augmentation

6. **Explainability**:
   - Grad-CAM visualizations
   - Attention maps

## 📝 Notes

- The model uses categorical crossentropy loss, so ensure labels are one-hot encoded
- Image preprocessing must match training (division by 255.0)
- For production use, consider adding input validation and error handling
- Monitor model performance on new data and retrain periodically

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Dataset source: [PlantVillage Dataset](https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset/data?select=color)
- Base model: MobV2
- tf lite : model.tflite
- Framework: TensorFlow/Keras

## 📧 Contact

For questions or feedback, please open an issue in the repository.

---

**Last Updated**: February 2026  
**Model Version**: 1.0  
**Framework**: TensorFlow 2.x
