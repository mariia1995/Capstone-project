
class Project:
    def __init__(self, name, user_id, id="", creation_date="", description=""):
        self.id = id
        self.name = name
        self.user_id = user_id
        self.description = description
        self.creation_date = creation_date


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            "user_id": self.user_id,
            'description': self.description,
            'creation_date': self.creation_date
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)