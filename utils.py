import os
import subprocess
import sublime

def find_bibfiles(open_filename):
    try:
        env = os.path.dirname(open_filename)
    except AttributeError:
        return None
    candidates = list(filter(lambda x: x.endswith('.bib'), os.listdir(env)))
    if candidates:
        bibfiles = [os.path.join(env, x) for x in candidates]
    else:
        bibfiles = list()

    return bibfiles

def process_open(command, stdin=None, stdout=None, stderr=None, cwd=None, env=None):
    if sublime.platform() == "windows":
        if isinstance(command, list):
            proc = subprocess.Popen(command, env=env, stdin=stdin, stdout=stdout, stderr=stderr, cwd=cwd, shell=True)
        else:
            proc = subprocess.Popen(command.split(" "), env=env, stdin=stdin, stdout=stdout, stderr=stderr, cwd=cwd, shell=True)
    else:
        if isinstance(command, list):
            proc = subprocess.Popen(" ".join(command), env=env, stdin=stdin, stdout=stdout, stderr=stderr, cwd=cwd, shell=True)
        else:
            proc = subprocess.Popen(command, env=env, stdin=stdin, stdout=stdout, stderr=stderr, cwd=cwd, shell=True)


    return proc