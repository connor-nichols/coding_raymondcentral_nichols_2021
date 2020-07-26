import os  # Used for managing files
import dataset  # Used for managing the databases in an easy to read way
import random
import string

databases = {  # Dictionary to store databases and their locations. Locations are also store in applicable objects.
    "Students": r"data\Students.db",  # Mirrored in Student class
    "Advisers": r"data\Advisers.db",  # Mirrored in Adviser class
    "Quizzes": r"data\Quizzes.db",  # Mirrored in Quiz class
    "Questions": r"data\Questions.db",  # Mirrored in Question class
    "Config": r"config\Config.db",  # Not mirrored. Used to store settings.
    "Roles": r"config\Roles.db"  # Allows assigning advisers various permissions.
}
folders = [r"data",  # Stores common folders. Any new additions since last run will be auto created by setup()
           r"backups",
           r"config"
           ]


def create_file(name):  # Gives us a way to create simple files.
    with open(name, "w+"):  # Using with closes the file for us, so it's ready for work
        return True  # Simply returns True to complete the function


def setup():  # Initial setup upon each run. Also performs first time setup, as well as any housekeeping.
    for folder in folders:  # Loops through list, creating folders if they don't exist. Loop prevents repetition.
        if os.path.exists(folder) is False:
            os.mkdir(folder)

    for database in databases:  # Similar functionality to above. Makes adding new files easy.
        file = databases[database]  # Creates this reference to improve readability
        if os.path.exists(file) is False:
            create_file(file)


class Student:  # What makes a student. Only required params are name and grade. All others can be auto generated.
    def __init__(self, name, grade, id_num=None, quizzes_taken=None, average_score=None):
        self.name = name
        self.id = id_num  # Defined up here so the lower items know about it. See note at bottom of class.
        self.grade = grade
        if quizzes_taken is None:
            self.quizzes_taken = str([])  # Formats as a list to prevent having to do this later. Stored as str for db.
        self.average_score = average_score

        self.database = databases["Students"]  # Mirrors the databases variable, so changes made there reflect here.
        self.table = "Students"  # Tells the program the table it needs.
        self.columns = [{"id": self.id},  # Defines columns in database. Allows generalization.
                        {"name": self.name},  # List of dicts allows easy unpacking to kwargs.
                        {"grade": self.grade},
                        {"quizzes_taken": self.quizzes_taken},
                        {"average_score": self.average_score}
                        ]
        self.unique_key = "id"  # Tells the program when it's searching what key should be used as a unique identifier.
        self.dict_form = {"id": self.id,  # Provides dictionary form of data in the object
                          "name": self.name,
                          "grade": self.grade,
                          "quizzes_taken": self.quizzes_taken,
                          "average_score": self.average_score
                          }

        self.primary_unique_index = 0  # Tells functions which item should be used to check uniqueness
        self.secondary_unique_index = 1  # Backup, mainly used for creating ids
        if self.id is None:
            self.id = create_ids(self)  # This is redefined so the items above don't conflict.
        # TODO: Could possibly create headaches later on. Keep that in mind. - Connor from the past

    def __call__(self):
        pass


class Adviser:
    def __init__(self, name, role, id_num = None):
        self.name = name
        self.id = id_num
        self.role = role
        # Usage variables
        self.database = databases["Advisers"]  # Mirrors the databases variable, so changes made there reflect here.
        self.table = "Advisers"  # Tells the program the table it needs.
        self.columns = [{"id": self.id},  # Defines columns in database. Allows generalization.
                        {"name": self.name},  # List of dicts allows easy unpacking to kwargs.
                        {"role": self.role}
                        ]
        self.unique_key = "id"  # Tells the program when it's searching what key should be used as a unique identifier.
        self.dict_form = {"id": self.id,  # Provides dictionary form of data in the object
                          "name": self.name,
                          "role": self.role
                          }

        self.primary_unique_index = 0  # Tells functions which item should be used to check uniqueness
        self.secondary_unique_index = 1  # Backup, mainly used for creating ids
        if id_num is None:
            self.id = create_ids(self)  # This is redefined so the items above don't conflict.
        # TODO: Could possibly create headaches later on. Keep that in mind. - Connor from the past


class Quiz:  # A quiz needs questions and an ID. We'll only create a quiz once, no duplicates
    def __init__(self, id_num: int, questions: list):
        self.id = create_ids(self)


class Answer:
    def __init__(self, text: dict, question_type, correct: bool):
        self.text = text
        self.type = question_type
        self.correct = correct


class Question:
    def __init__(self, text: str, question_type):
        self.text = text
        self.type = question_type
        self.answers = {}

        if self.type == "matching" or "multiple_choice":
            self.keys = list(string.ascii_lowercase)

    def add_answer(self, answer: Answer):
        if self.type == "matching":
            for key in answer.text.keys():
                print(key)
                if key not in self.keys:
                    return False
                else:
                    self.answers.update(answer.text)



def create_ids(new_object):
    check = unique_check(new_object, return_mode=True, use_secondary=True)  # We need to use secondary since no id yet
    print(check)
    if check == []:  # Nothing was found by the unique check, so we need to generate an ID
        potential_id = random.randint(10000000, 99999999)
        new_object.id = potential_id  # Sets the objects id to the new ID so we can run unique check again
        check = unique_check(new_object)  # We're checking the ID and don't need anything back, so defaults are fine.
        if check:
            return potential_id
        else:
            create_ids(new_object)  # Tries again.
    elif check != [] and not isinstance(check, bool):  # Something was found by unique check, so we'll return the ID
        return check[0]["id"]
    else:
        return False


def return_table(query):
    if isinstance(query, str):  # Checks to see if we were provided a string
        if query in databases.keys():
            db = dataset.connect(f"sqlite:///{databases[query]}")
            return db[query]
        else:
            return False
    if object_valid(query):  # If we got an object use that syntax
        db = dataset.connect(f"sqlite:///{query.database}")
        return db[query.table]


def object_valid(object_check):  # Checks to see if parameter is a valid object.
    if isinstance(object_check, (Student, Adviser, Quiz, Question, Answer)):
        return True
    else:
        return False


# return_mode tells the function to return what it found. use_secondary tells the code to use the secondary unique index


def unique_check(object_check, return_mode=False, use_secondary=False):
    if object_valid(object_check):  # Makes sure we're working with an object
        table = return_table(object_check)
        if use_secondary:
            index = object_check.secondary_unique_index  # Switches to using secondary index if we need
        else:
            index = object_check.primary_unique_index
        check = table.find(**object_check.columns[index])  # Unpacks whatever item we want to search for
        items = []
        for item in check:
            items.append(item)  # Appends each result to a list
        if len(items) < 2:
            if return_mode:
                return items  # Returns what it found, if anything. Will return blank list if nothing found.
            else:
                return True  # Simply returns true if unique and return_mode is False.
        else:
            return False  # Returns False if two or more results


def add_edit_items(add_object):  # Uses upsert to insert items if they don't exist, and update them if they do.
    table = return_table(add_object)
    if unique_check(add_object, use_secondary=True):
        table.upsert(add_object.dict_form, [add_object.unique_key])


setup()

test = Question("Who am I?", "matching")

test.add_answer(Answer({"a": "Connor"}, "matching", True))
print(test.add_answer(Answer({"a": "Connor"}, "matching", True)))
print(test.answers)