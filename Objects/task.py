
class Task:
    def __init__(self, name, creator_id, assignee, project_id, due_date, status_id=1, id="", creation_date="", description=""):
        self.id = id
        self.name = name
        self.creator_id = creator_id
        self.assignee = assignee
        self.project_id = project_id
        self.status_id = status_id
        self.due_date = due_date
        self.description = description
        self.creation_date = creation_date


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            "creator_id": self.creator_id,
            "assignee": self.assignee,
            "project_id": self.project_id,
            "status_id": self.status_id,
            "due_date": self.due_date,
            'description': self.description,
            'creation_date': self.creation_date
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)