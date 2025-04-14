from flask import Flask, render_template, request
from keras.src.applications.mobilenet_v2 import MobileNetV2
from forms import UploadForm
from config import Config
from utils import clear_uploads_dir, split_image, generate_histograms, verify_recaptcha, classify_image
import os
import uuid

app = Flask(__name__)
app.config.from_object(Config)

# Очистка папки uploads при запуске
clear_uploads_dir(app.config['UPLOADS_DIR'])

# Загрузка модели MobileNetV2
model = MobileNetV2(weights='imagenet')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()
    recaptcha_sitekey = app.config['RECAPTCHA_SITE_KEY']

    if form.validate_on_submit():
        # Проверка reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response:
            return "Пожалуйста, пройдите проверку reCAPTCHA", 400
        if not verify_recaptcha(recaptcha_response, app.config['RECAPTCHA_SECRET_KEY']):
            return "Проверка reCAPTCHA не пройдена", 400

        file = form.image.data
        # Создание уникальной папки для загрузки
        upload_dir = os.path.join(app.config['UPLOADS_DIR'], str(uuid.uuid4()))
        os.makedirs(upload_dir, exist_ok=True)

        # Сохранение исходного изображения
        original_path = os.path.join(upload_dir, 'original.jpg')
        file.save(original_path)

        # Разделение на 4 части
        parts = split_image(original_path)
        for i, part in enumerate(parts, 1):
            part.save(os.path.join(upload_dir, f'part{i}.jpg'))

        # Создание гистограмм
        generate_histograms(original_path, upload_dir)
        for i in range(1, 5):
            generate_histograms(os.path.join(upload_dir, f'part{i}.jpg'), upload_dir)

        # Классификация изображения
        classification = classify_image(original_path, model)

        # Отображение результата
        return render_template('result.html', uuid=os.path.basename(upload_dir), classification=classification)

    return render_template('upload.html', form=form, recaptcha_sitekey=recaptcha_sitekey)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)