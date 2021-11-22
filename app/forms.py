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
    nextsub = SubmitField("Submit & Next Article")
    homesub = SubmitField("Submit & Return Home")


class AutoPopForm(FlaskForm):
    url0 = StringField("Url1")
    url1 = StringField("Url2")
    url2 = StringField("Url3")
    url3 = StringField("Url4")
    url4 = StringField("Url5")
    url5 = StringField("Url6")
    url6 = StringField("Url7")
    submit = SubmitField("submit urls")
