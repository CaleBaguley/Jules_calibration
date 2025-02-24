"""
General file management code.
"""
import os
from logging import exception


def make_folder(new_folder,
                overwrite_existing=False):

    """
    Creates a new folder.
    :param new_folder: target address of the new folder (str)
    :param overwrite_existing: If True, overwrites the existing folder (bool)
    :return: new_folder address (str)
    """

    new_folder = os.getcwd() + "/tmp/output/"
    if(os.path.exists(new_folder)):
        if overwrite_existing:
            # Walk through the directory and delete all files
            for root, dirs, files in os.walk(new_folder, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(new_folder)
        else:
            exception(f"ERROR: {new_folder} folder already exists.\n"
                      + "Please delete the folder or set overwrite_tmp_files = True.\n")
    os.mkdir(new_folder)

    return new_folder