from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import app, db


app.secret_key = 'b103e2de4f62e587e7ed7fae5f9cf13b'
app.config['SQLALCHEMY_DATABASE_URI']= "postgres://pjmykvtzkrrksq:d01d3cb8bd6dc423ba7d321bc53fbc44cb824848ae03cabb2a2c3b706c654cfd@ec2-52-44-55-63.compute-1.amazonaws.com:5432/d7vr8mr3co5icq"

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
