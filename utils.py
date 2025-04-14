import os
import uuid
import shutil
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from keras.src.applications.mobilenet_v2 import preprocess_input, decode_predictions

def clear_uploads_dir(uploads_dir):
    """Очистка и создание папки uploads."""
    if os.path.exists(uploads_dir):
        shutil.rmtree(uploads_dir)
    os.makedirs(uploads_dir, exist_ok=True)

def split_image(img_path):
    """Разделение изображения на 4 части."""
    img = Image.open(img_path)
    width, height = img.size
    return [
        img.crop((0, 0, width // 2, height // 2)),  # Верхний левый
        img.crop((width // 2, 0, width, height // 2)),  # Верхний правый
        img.crop((0, height // 2, width // 2, height)),  # Нижний левый
        img.crop((width // 2, height // 2, width, height))  # Нижний правый
    ]

def generate_histograms(img_path, save_dir):
    """Создание гистограмм для изображения."""
    img = Image.open(img_path)
    filename = os.path.basename(img_path)
    prefix = os.path.splitext(filename)[0]
    r, g, b = img.split()
    for channel, color in zip([r, g, b], ['red', 'green', 'blue']):
        hist = channel.histogram()
        plt.figure()
        plt.bar(range(256), hist, color=color)
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        plt.title(f'{color} Histogram')
        plt.savefig(os.path.join(save_dir, f'{prefix}_{color}.png'))
        plt.close()

def verify_recaptcha(recaptcha_response, secret_key):
    """Проверка reCAPTCHA."""
    payload = {'secret': secret_key, 'response': recaptcha_response}
    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload, timeout=5)
        result = response.json()
        return result.get('success', False)
    except (requests.RequestException, ValueError) as e:
        print(f"reCAPTCHA verification error: {str(e)}")
        return False

def classify_image(img_path, model):
    """Классификация изображения с помощью MobileNetV2."""
    img = Image.open(img_path).resize((224, 224))
    img_array = np.array(img)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    predictions = model.predict(img_array)
    decoded_predictions = decode_predictions(predictions, top=3)[0]
    return ', '.join([f'{label}: {prob:.2f}' for _, label, prob in decoded_predictions])