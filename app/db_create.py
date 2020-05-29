from app import db
from app.models import *

print ("initialised")
db.create_all()
print ("create_all")
db.session.add(User('admin', 'admin', 'admin', 0))
print ("session.add")
db.session.commit()
print ("session.commit")
