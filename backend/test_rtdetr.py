"""
Test script to verify RT-DETR model integration
"""
import os
# Force python implementation for protobuf
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
# Disable TensorFlow conflicts
os.environ['USE_TF'] = 'NO'
os.environ['USE_TORCH'] = 'YES'

from transformers import AutoImageProcessor, AutoModelForObjectDetection
from PIL import Image
import torch

print("Testing RT-DETR Model Integration...")
print("-" * 50)

# Model name
model_name = "PekingU/rtdetr_r18vd"

print(f"Loading model: {model_name}")

# Load processor and model
processor = AutoImageProcessor.from_pretrained(model_name)
model = AutoModelForObjectDetection.from_pretrained(model_name)

# Check device
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

model.to(device)
model.eval()

print("\n✅ Model loaded successfully!")
print(f"✅ Processor type: {type(processor).__name__}")
print(f"✅ Model type: {type(model).__name__}")
print(f"✅ Number of labels: {len(model.config.id2label)}")

print("\nSample labels:")
for i in range(min(10, len(model.config.id2label))):
    print(f"  {i}: {model.config.id2label[i]}")

print("\n" + "=" * 50)
print("RT-DETR model is ready to use!")
print("=" * 50)
