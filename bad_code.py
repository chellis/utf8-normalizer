# This file is meant to trigger bandit analysis failures


def bad_try_except():
    try:
        trial = 'Bah humbug'
    except:
        pass


def bad_password():
    password = 'something hardcoded'
    username = 'something else hardcoded'
    return username, password


def use_eval():
    eval('print(345)')
