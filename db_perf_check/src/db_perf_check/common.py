from random import randint, shuffle
from time import time


def get_key_elements(name: str, single: bool, num_of_elements: int = 10000) -> str | list:
    from_ = 1
    to_ = num_of_elements
    if single:
        return f'{name}{randint(from_, to_) :05d}'
    else:
        lst = [
            f'{name}{i :05d}'
            for i in range(from_, to_ + 1)
        ]
        shuffle(lst)
        return lst


def generate_value(
        pref_name: str,
        suff_name: str,
        to_pref: int,
        to_suff: int,
        max_number_of_relations: int = 10,
        sep: str = '/',
    ) -> str:
    rels = []
    for _ in range(randint(1, max_number_of_relations)):
        rels.append(
            [
                get_key_elements(pref_name, True, to_pref),
                get_key_elements(suff_name, True, to_suff),
            ]
        )
    return {
        'created_at': int(time()),
        'related_elements': [
            f'{pref}{sep}{suff}'
            for pref, suff in rels
        ]
    }
