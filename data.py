import pickle
from pathlib import Path

'''
dict {
    namedtuple(1, 2, ...): datetime
}

IF namedtuple in dict
THEN use timedelta on datetime

Why use pickle instead of JSON?
I don't care, that's why.
'''

def pickle_dict_load(fp: Path) -> dict: # size constraints are for the weak
    if not fp.is_file():
        return {}
    
    with open(fp, 'rb') as fd:
        data = pickle.load(fd)

    if not isinstance(data, dict):
        raise TypeError(f'expected dict, got {type(data).__name__}')
    
    return data

def pickle_dict_dump(obj: dict, fp: Path):
    with open(fp, 'wb') as fd:
        pickle.dump(obj, fd)
