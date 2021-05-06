from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class ArticleForm(FlaskForm):

    url = StringField("Url", validators=[DataRequired()])
    title = StringField("Headline", validators=[DataRequired()])
    author = StringField("Authors", validators=[DataRequired()])
    body = TextAreaField("Body", validators=[DataRequired()])
    source = StringField("Source")
    date = StringField("Date of article", validators=[DataRequired()])
    homesub = SubmitField("Submit & Return Home")
    nextsub = SubmitField("Submit another article")


class AutoPopForm(FlaskForm):
    url0 = StringField("Url0")
    url1 = StringField("Url1")
    url2 = StringField("Url2")
    url3 = StringField("Url3")
    url4 = StringField("Url4")
    url5 = StringField("Url5")
    url6 = StringField("Url6")
    submit = SubmitField("submit urls")
