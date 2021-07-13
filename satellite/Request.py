from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.String(100))
    time = db.Column(db.DateTime(timezone=True),
                     default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Request(file_id='%s', time='%s')>" % (
            self.file_id, self.time)
