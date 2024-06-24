import sqlalchemy as sqlalc
import sqlalchemy.orm as sqlorm
from app import app, db #importing flask and database
from app.models import User, Post #importing functions

@app.shell_context_processor
def make_shell_context():
    return {'sqlalc':sqlalc, 'sqlorm': sqlorm, 'db': db, 'User': User, 'Post':Post} 