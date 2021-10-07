from app import db, TODAY
# from sqlalchemy.dialects.postgresql import JSON
# Todo: add users

class Articles(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.Text)
    authors = db.Column(db.String(200))
    source = db.Column(db.String(100))
    url = db.Column(db.String(200))
    # date is not super important so no need to worry about utc for now
    artdate = db.Column(db.Date, default=TODAY)
    briefingdate = db.Column(db.Date, nullable=False, default=TODAY)
    ranking = db.Column(db.Integer, nullable=False, default=1)
    # linked list pointing to next article?
    nextart = db.Column(db.Integer)
    prevart = db.Column(db.Integer)


    # def __init__(self, title, body, authors, source, url, artdate, briefingdate, ranking, nextart, prevart):
    #     self.title = title
    #     self.body = body
    #     self.authors = authors
    #     self.source = source
    #     self.url = url
    #     self.artdate = artdate
    #     self.briefingdate = briefingdate
    #     self,ranking = ranking
    #     self.nextart = nextart
    #     self.prevart = prevart



    def __repr__(self):
        return f"{self.title}, {self.source}, {self.id}"

# UPDATING DATABASE
# db.create_all()
# db.session.add(Article)
# db.session.commit()
