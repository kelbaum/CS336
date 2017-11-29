'''The basic user model (For logins)

written by: Zachary Blanco
tested by: Zachary Blanco
debugged by: Zachary Blanco

The users will have roles i.e. chef, manager, host, waitress, etc..
'''
from peewee import CharField, IntegrityError
from asst.models import BaseModel
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class User(UserMixin, BaseModel):
    '''A User model for who will be using the software. Users have different levels of access with different roles

    Current active roles:

        - customer
        - manager
    '''
    email = CharField()
    password = CharField()
    name = CharField()
    address = CharField()
    phone_no = CharField()
    role = CharField() #assumption that user will enter valid role

    @classmethod
    def create_user(cls, email, password, name, role):
        '''Creates a new user

        Args:
            email(str): The user email
            password(str): The password string - no need to hash beforehand
            name(str): name, doesn't have to be unique
            address(str): address of the user
            phone_no(str): phone number of the user
            role(str): The user role. admin, manager, chef, host, etc..

        Returns:
            N/A

        Raises:
            ValueError: When cid already exists
        '''

        try:
            cls.create(
                email=email,
                password=generate_password_hash(password),
                name=name,
                phone_no = phone_no,
                address = address,
                role=role)
        except IntegrityError:
            raise ValueError("User already exists")
