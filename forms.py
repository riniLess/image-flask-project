from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class UploadForm(FlaskForm):
    image = FileField('Image', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'png'], 'Only JPG or PNG files are allowed!')
    ])
    submit = SubmitField('Upload')