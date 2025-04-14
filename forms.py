from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class UploadForm(FlaskForm):
    image = FileField('Image', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'png'], 'Только JPG или PNG!')
    ])
    submit = SubmitField('Upload')