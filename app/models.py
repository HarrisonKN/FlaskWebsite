#this file provides the database structure for the application
from time import time
from datetime import datetime, timezone
from typing import Optional
import jwt
import sqlalchemy as sqlalc
import sqlalchemy.orm as sqlorm
from app import db
from app import login
from app import app

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

followers = sqlalc.Table(
    'followers', db.metadata,
    sqlalc.Column('follower_id', sqlalc.Integer, sqlalc.ForeignKey('user.id'), primary_key=True),
    sqlalc.Column('followed_id', sqlalc.Integer, sqlalc.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id: sqlorm.Mapped[int] = sqlorm.mapped_column(primary_key=True)
    username: sqlorm.Mapped[str] = sqlorm.mapped_column(sqlalc.String(64),
                                                        index=True,
                                                        unique=True)
    email: sqlorm.Mapped[str] = sqlorm.mapped_column(sqlalc.String(120),
                                                     index=True,
                                                     unique=True)
    password_hash: sqlorm.Mapped[Optional[str]] = sqlorm.mapped_column(sqlalc.String(256))
    posts: sqlorm.WriteOnlyMapped['Post'] = sqlorm.relationship(
        back_populates='author')
    about_me: sqlorm.Mapped[Optional[str]] = sqlorm.mapped_column(sqlalc.String(140))
    last_seen: sqlorm.Mapped[Optional[datetime]] = sqlorm.mapped_column(
        default=lambda: datetime.now(timezone.utc))

    following: sqlorm.WriteOnlyMapped['User'] = sqlorm.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id==id),
        secondaryjoin=(followers.c.followed_id==id),
        back_populates='followers')
    followers: sqlorm.WriteOnlyMapped['User'] = sqlorm.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id==id),
        secondaryjoin=(followers.c.follower_id==id),
        back_populates='following')

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return ',User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id==user.id)
        return db.session.scalar(query)
    
    def followers_count(self):
        query = sqlalc.select(sqlalc.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = sqlalc.select(sqlalc.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)
    
    def following_posts(self):
        Author = sqlorm.aliased(User)
        Follower = sqlorm.aliased(User)
        return (
            sqlalc.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sqlalc.or_(
                Follower.id==self.id,
                Author.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User,id)
    
class Post(db.Model):
    id: sqlorm.Mapped[int] = sqlorm.mapped_column(primary_key=True)
    body: sqlorm.Mapped[str] = sqlorm.mapped_column(sqlalc.String(140))
    timestamp: sqlorm.Mapped[datetime] = sqlorm.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id : sqlorm.Mapped[int] = sqlorm.mapped_column(sqlalc.ForeignKey(User.id), index=True)
    author: sqlorm.Mapped[User] = sqlorm.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)