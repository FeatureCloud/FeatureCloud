import os


def getcwd_fslash():
    """
    Returns the current working directory and makes sure it contains forward slashes as separator.
    Hint: os.getcwd() result contains backslashes on Windows.
    """
    return os.getcwd().replace("\\", "/")
