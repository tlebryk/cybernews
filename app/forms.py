from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Length


class ArticleForm(FlaskForm):
    """ Manual entry form"""
    url = StringField("Url", validators=[DataRequired()])
    title = StringField("Headline", validators=[DataRequired()])
    author = StringField("Authors", validators=[DataRequired()])
    body = TextAreaField("Body", validators=[DataRequired()])
    source = StringField("Source")
    date = DateTimeField("Date of article", format="%B %d, %Y", validators=[DataRequired()])
    # prevsub = SubmitField("Submit & Next Article")
    nextsub = SubmitField("Submit & Next Article")
    homesub = SubmitField("Submit & Return Home")


class AutoPopForm(FlaskForm):
    """ Form to send urls to Zotero server"""
    url0 = StringField("Url1")
    url1 = StringField("Url2")
    url2 = StringField("Url3")
    url3 = StringField("Url4")
    url4 = StringField("Url5")
    url5 = StringField("Url6")
    url6 = StringField("Url7")
    submit = SubmitField("submit urls")
