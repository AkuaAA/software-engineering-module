from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    Opportunity = db.relationship('Opportunity')
    role = db.Column(db.String(10), default='user')  # 'admin' for superuser, 'user' for normal user
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    body = db.Column(db.String(1000))

   