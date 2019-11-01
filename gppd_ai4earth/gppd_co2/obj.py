""" This file contains saving, loading, and other misc. scripts using JSON to save objects into
a readable format, such as a text file.
"""

import json

def save(obj, name):
    """
    Paramaters
    obj: container-like; objects such as lists, dictionaries, arrays, etc
    name: string; the name to save the object as, including the path

    Usage
    import gppd_co2.obj as obj
    my_list = [i for i in range(10)]
    obj.save(my_list, '/path/to/file.txt')

    Notes
    This will overwrite whatever file exists with the same name. Uses JSON to
    save files.
    """

    with open(name, 'w+') as file_:
        json.dump(obj, file_)


def load(name):
    """
    Given a path to the object, loads the data and returns the object

    Parameters
    name: string, path to the object

    Usage
    from gppd_co2 import obj
    my_dict = obj.load('../my/dict/file.txt')

    Notes
    Uses JSON to load the file.
    """

    with open(name, 'r') as file_:
        return json.load(file_)

class BijectiveDict(dict):
    """
    References
    https://stackoverflow.com/questions/1456373/two-way-reverse-map
    """
    def __init__(self, dict_={}):
        assert isinstance(dict_, dict), "Argument Error: dict_ is not of type dict"

        for key, val in dict_.items():
            self.update(key, val)

    def __setitem__(self, x, y):
        # override how self[key] = value works since this class inherits Dict.
        # this way, self.add can work as expected

        # delete any old pairs that contain x or y
        if x in self:
            del self[x]
        if y in self:
            del self[y]

        dict.__setitem__(self, x, y)
        dict.__setitem__(self, y, x)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)

    def __len__(self):
        # returns number of connections
        return dict.__len__(self) // 2

    def __dir__(self):
        return ["update"]

    def update(self, x, y):
        """ This will overwrite what was in the dictionary previously
        so make sure to change assignment of the old values if you want to
        keep them.
        """
        self[x] = y

    # TODO: unique(), pop(), clear()



