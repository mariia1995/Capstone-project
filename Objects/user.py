from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, username, email="", first_name="", last_name="", birthdate="", phone_number="", availability=100):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.birthdate = birthdate
        self.phone_number = phone_number
        self.availability = availability

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birthdate': self.birthdate,
            'phone_number': self.phone_number,
            'availability': self.availability
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    # test the API

