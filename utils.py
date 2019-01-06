import os

def find_bibfiles(open_filename):
    env = os.path.dirname(open_filename)
    candidates = list(filter(lambda x: x.endswith('.bib'), os.listdir(env)))
    if candidates:
        bibfiles = [os.path.join(env, x) for x in candidates]
    else:
        bibfiles = list()

    return bibfiles