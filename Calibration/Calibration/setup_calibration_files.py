"""
Contains functions used to set up folders needed by the calibration process
"""

import os
from Calibration.general.file_management import make_folder
from Calibration.Namelist_management.Duplicate import duplicate
from Calibration.Namelist_management.Edit_variable import edit_variable
from logging import exception

def setup_calibration_run_folders(master_namelist_address,
                                  output_folder,
                                  variable_names,
                                  tmp_folder = None,
                                  overwrite_existing_folders = False,
                                  use_existing_run_info = False,
                                  setup_dump_files = False):

    """
    Sets up the folders needed for the calibration process
    :param master_namelist_address:
    :param output_folder:
    :param tmp_folder:
    :param overwrite_existing_folders:
    :param use_existing_run_info:
    :param setup_dump_files:
    :return:
    """

    # Set up the temporary folders
    tmp_folder = setup_tmp_folders(master_namelist_address,
                                   tmp_folder,
                                   overwrite_existing_folders)

    # Set up the output files
    output_folder = setup_output_files(output_folder,
                                       variable_names,
                                       overwrite_existing_folders,
                                       use_existing_run_info,
                                       setup_dump_files)

    return tmp_folder, output_folder

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

    print(f"Setting up temporary folders in {tmp_folder}")

    # Creat a temporary folder
    make_folder(tmp_folder,
                overwrite_existing=overwrite_existing_folders)

    # Add a folder for the namelist files
    #tmp_namelist = make_folder(tmp_folder + ("namelist/"),
    #                           overwrite_existing=overwrite_existing_folders)

    # Add a folder for the JULES output
    tmp_output = make_folder(tmp_folder + "output/",
                             overwrite_existing=overwrite_existing_folders)

    # Coppy the namelist files to the temporary folder
    duplicate(master_namelist_address,
              tmp_folder + ("namelist"),
              overwrite=overwrite_existing_folders)

    # Change the JULES output to the temporary folder
    # Note we need to add ' to both ends of the output directory.
    edit_variable(tmp_folder + ("namelist/") + "output.nml",
                  "jules_output",
                  "output_dir",
                  "'" + tmp_output + "'")

    return tmp_folder


def setup_output_files(output_folder,
                       variable_names,
                       overwrite_existing_folders = False,
                       use_existing_run_info = False,
                       setup_dump_file_folder = False):

    """
    Creates the output files needed for the calibration process
    :param output_folder: folder address for the output files (str)
    :param variable_names: names of the variables to store in the run metadata file (list of str)
    :param overwrite_existing_folders: If True, overwrites the existing folders (bool)
    :param use_existing_run_info: If True, use existing run_info file (bool)
    :return: output_folder (str)
    """

    # Create the output folder
    output_folder = make_folder(output_folder,
                                overwrite_existing=overwrite_existing_folders)

    # Create the dump folder
    if setup_dump_file_folder:
        make_folder(output_folder + "dump/",
                    overwrite_existing=overwrite_existing_folders)

    # -- Metadata file setup ---------------------------------------------------
    # Does the file already exist?
    if os.path.exists(output_folder + "run_info.csv"):
        # Check if the user wants to append to the file
        if use_existing_run_info:
            # Check the file has the correct header
            header = "run_id,run_date," + ",".join(variable_names) + "\n"

            with open(output_folder + "run_info.csv", "r") as run_info:
                if run_info.readline() != header:
                    exception(f"ERROR: {output_folder}run_info.csv file already exists but has the wrong header.")
                    return None

            print(f"{output_folder}run_info.csv file already exists, appending data.")

        else:
            exception(f"ERROR: {output_folder}run_info.csv file already exists.\n"
                      + "Please delete the file or set append_to_run_info = True.\n")
    else:
        print(f"Creating {output_folder}run_info.csv file")
        with (open(output_folder + "run_info.csv", "w") as run_info):
            # write header
            header = "run_id,run_date"
            header += "," + ",".join(variable_names)
            header += "\n"
            run_info.write(header)

    return output_folder
