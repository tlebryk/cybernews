from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ArticleForm(FlaskForm):

    url = StringField("Url", validators=[DataRequired()])
    title = StringField("Headline", validators=[DataRequired()])
    author = StringField("Authors", validators=[DataRequired()])
    body = StringField("Body", validators=[DataRequired()])
    source = StringField("Source")
    date = StringField("Date of article", validators=[DataRequired()])


    submit = SubmitField("submit article")
