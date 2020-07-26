import os
import dataset


class Student:
    def __init__(self, name, id_num, grade, quizzes_taken=None, average_score=None):
        self.name = name
        self.id = id_num  # TODO: temp stand in until id creation works
        self.grade = grade
        if quizzes_taken is None:
            self.quizzes_taken = []  # Formats as a list to prevent having to do this later
        self.average_score = average_score


class Adviser:
    pass


class Quiz:
    pass


class Question:
    pass


class Answer:
    pass


def setup():
    pass