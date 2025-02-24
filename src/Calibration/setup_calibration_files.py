"""
Contains functions used to set up folders needed by the calibration process
"""

import os
from src.general.file_management import make_folder
from src.Namelist_management.Duplicate import duplicate
from src.Namelist_management.Edit_variable import edit_variable

def setup_tmp_folders(master_namelist_address,
                      tmp_folder = None,
                      overwrite_existing_folders = False):
    """
    Creates the temporary folders needed for the calibration process
    :param master_namelist_address: Address of the master namelist file (str)
    :param tmp_folder: Address of the temporary folder (str)
    :param overwrite_existing_folders: If True, overwrites the existing folders (bool)
    """

    if tmp_folder is None:
        tmp_folder = os.getcwd() + "/tmp/"

    # Creat a temporary folder
    make_folder(tmp_folder,
                overwrite_existing=overwrite_existing_folders)

    # Add a folder for the namelist files
    tmp_namelist = make_folder(tmp_folder + ("namelist/"),
                               overwrite_existing=overwrite_existing_folders)

    # Add a folder for the JULES output
    tmp_output = make_folder(os.getcwd() + "/tmp/output/",
                             overwrite_existing=overwrite_existing_folders)

    # Coppy the namelist files to the temporary folder
    duplicate(master_namelist_address,
              tmp_namelist,
              overwrite=overwrite_existing_folders)

    # Change the JULES output to the temporary folder
    # Note we need to add ' to both ends of the output directory.
    edit_variable(tmp_namelist + "output.nml",
                  "jules_output",
                  "output_dir",
                  "'" + tmp_output + "'")

    return tmp_folder
