from app import db, TODAY




# Todo: add users

class Articles(db.Model):
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

    def __repr__(self):
        return f"{self.title}, {self.source}, {self.id}"

# UPDATEING DATABASE
# db.create_all()
# db.session.add(Article)
# db.session.commit()

# QUERYING DATABASE
# Article.querry.all()/.first()/.get(id)/filter_by(attribute="someval").all()