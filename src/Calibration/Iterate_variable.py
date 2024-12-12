"""
Code to run JULES using a series of values for a given variable
"""
import os
from logging import exception

import src.Namelist_management.Duplicate as Duplicate
import src.Run_JULES.Run_JULES as Run_JULES
import src.Namelist_management.Edit_variable as Edit_variable
import src.Namelist_management.Read as Read


def iterate_variables(jules_executable_address,
                      master_namelist_address,
                      variable_names,
                      variable_namelists,
                      variable_namelist_files,
                      variable_values,
                      output_folder,
                      run_id_prefix,
                      keep_dump_files = False,
                      overwrite_tmp_files = False):

    """
    Iterate over a series of values for a given variable
    :param jules_executable_address: JULES executable address (str)
    :param master_namelist_address:  of the folder containing all the namelists to copy (str)
    :param variable_names: Variable to change (str)
        or list of variables to change (list of str)
    :param variable_namelists: Name of the namelist containing the changing variable (str)
        or list of namelists (list of str)
    :param variable_namelist_files: Name of the namelist file containing the changing variable (str)
        or list of namelist files (list of str)
    :param variable_values: Values of the variable to iterate over as a 1D list of strings (list of strings)
        or lait of lists containing each set of variable values to try (list of lists of str)
    :param output_folder: Location of output folder (str)
    :param run_id_prefix: Prefix for all run ids (str)
    :param keep_dump_files: If True, keeps the JULES dump files (bool) (optional)
    :return:
    """

    # Manage the case where the user only wants to iterate over one variable
    if type(variable_names) is str:
        variable_names = [variable_names]
        variable_namelists = [variable_namelists]
        variable_namelist_files = [variable_namelist_files]
        variable_values = [variable_values]

    # Make coppy of the master namelist to edit
    tmp_folder = os.getcwd() + "/tmp/"
    tmp_namelist = os.getcwd() + ("/tmp/namelist/")
    Duplicate.duplicate(master_namelist_address, tmp_namelist, overwrite=overwrite_tmp_files)

    # Create a temporary output folder
    tmp_output = os.getcwd() + "/tmp/output/"
    if(os.path.exists(tmp_output)):
        if overwrite_tmp_files:
            # Walk through the directory and delete all files
            for root, dirs, files in os.walk(tmp_output, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(tmp_output)
        else:
            exception("ERROR: temporary output folder already exists.\n"
                      + "Please delete the folder or set overwrite_tmp_files = True.\n")
    os.mkdir(tmp_output)

    # Create a list of the full file paths for the namelists to change
    variable_namelist_files_full = [tmp_namelist + file for file in variable_namelist_files]

    # Change the JULES output to a temporary folder
    # Note we need to add ' to both ends of the output directory.
    Edit_variable.edit_variable(tmp_namelist + "output.nml",
                                "jules_output",
                                "output_dir",
                                "'" + tmp_output + "'")

    # Check the actual output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get the output profile name
    profile_name = Read.read_variable(tmp_namelist + "output.nml",
                                      "jules_output_profile",
                                      "profile_name")

    # Remove any quotes from the profile name
    profile_name = profile_name.strip("'")
    profile_name = profile_name.strip('"')


    # Iterate over the values
    for i, values in enumerate(variable_values):

        # Edit the variable
        Edit_variable.edit_variable(variable_namelist_files_full,
                                    variable_namelists,
                                    variable_names,
                                    values)

        # Set the current run id
        current_run_id = run_id_prefix + f"_{i}"

        Edit_variable.edit_variable(tmp_namelist + "output.nml",
                                    "jules_output",
                                    "run_id",
                                    "'" + current_run_id + "'")

        # Run JULES
        Run_JULES.run_JULES(jules_executable_address, tmp_namelist)

        # Move the output from the temporary folder to the output folder
        os.rename(tmp_output + current_run_id + "." + profile_name + ".nc",
                  output_folder + current_run_id + "." + profile_name + ".nc")

        # If user wants to keep dump files, move them to the output folder
        if keep_dump_files:

            # Make a folder for the dump files
            current_dump_folder = output_folder + "/" + current_run_id + "_dump/"
            os.mkdir(current_dump_folder)

            output_files = os.listdir(tmp_output)
            for file in output_files:
                if 'dump' in file:
                    os.rename(tmp_output + file, current_dump_folder + file)

        # Delete the temporary output folder contents
        output_files = os.listdir(tmp_output)
        for file in output_files:
            os.remove(tmp_output + file)

    # Remove tmp folder and contents
    for root, dirs, files in os.walk(tmp_folder, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(tmp_folder)

    return

def iterate_soil_variable(jules_executable_address,
                          master_namelist_address,
                          soil_ancillary_address,
                          variable_name,
                          variable_values,
                          output_folder,
                          run_ids,
                          keep_dump_files = False,
                          overwrite_tmp_files = False):

    """
    Iterate over a series of values for a given soil variable
    :param jules_executable_address: file address of the JULES executable (str)
    :param master_namelist_address: folder containing the namelists to copy (str)
    :param soil_ancillary_address: soil ancillary file to use (str)
    :param variable_name: variable to iterate over (str)
    :param variable_values: values to iterate over (list of str)
    :param output_folder: JULES output folder (str)
    :param run_ids: name of each run (list of str)
    :param keep_dump_files: save JULES dumpfiles (bool)
    :param overwrite_tmp_files: overwrite any existing tmp files (bool)
    :return:
    """

    # Make a coppy of the master namelist to edit
    tmp_folder = os.getcwd() + "/tmp/"
    tmp_namelist = os.getcwd() + "/tmp/namelist/"
    Duplicate.duplicate(master_namelist_address, tmp_namelist, overwrite=overwrite_tmp_files)

    # Make a copy of the soil ancillary file
    tmp_soil_file = Duplicate.duplicate_soil_ancillary(soil_ancillary_address,
                                                       tmp_folder,
                                                       tmp_namelist + "ancillaries.nml",
                                                       overwrite=overwrite_tmp_files)

    # Create a temporary output folder
    tmp_output = os.getcwd() + "/tmp/output/"
    if (os.path.exists(tmp_output)):
        if overwrite_tmp_files:
            # Walk through the directory and delete all files
            for root, dirs, files in os.walk(tmp_output, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(tmp_output)
        else:
            exception("ERROR: temporary output folder already exists.\n"
                      + "Please delete the folder or set overwrite_tmp_files = True.\n")
    os.mkdir(tmp_output)

    # Change the JULES output to a temporary folder
    # Note we need to add ' to both ends of the output directory.
    Edit_variable.edit_variable(tmp_namelist + "output.nml",
                                "jules_output",
                                "output_dir",
                                "'" + tmp_output + "'")

    # Make the actual output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get the output profile name
    profile_name = Read.read_variable(tmp_namelist + "output.nml",
                                      "jules_output_profile",
                                      "profile_name")

    # Remove any quotes from the profile name
    profile_name = profile_name.strip("'")
    profile_name = profile_name.strip('"')

    # Iterate over the values
    for i, value in enumerate(variable_values):

        # Edit the variable
        Edit_variable.edit_soil_variable(tmp_soil_file,
                                         variable_name,
                                         value,
                                         tmp_namelist + "ancillaries.nml")

        # Set the current run id
        current_run_id = run_ids[i]

        Edit_variable.edit_variable(tmp_namelist + "output.nml",
                                    "jules_output",
                                    "run_id",
                                    "'" + current_run_id + "'")

        # Run JULES
        Run_JULES.run_JULES(jules_executable_address, tmp_namelist)

        # Move the output from the temporary folder to the output folder
        os.rename(tmp_output + current_run_id + "." + profile_name + ".nc",
                  output_folder + current_run_id + "." + profile_name + ".nc")

        # If user wants to keep dump files, move them to the output folder
        if keep_dump_files:

            # Make a folder for the dump files
            current_dump_folder = output_folder + "/" + current_run_id + "_dump/"
            os.mkdir(current_dump_folder)

            output_files = os.listdir(tmp_output)
            for file in output_files:
                if 'dump' in file:
                    os.rename(tmp_output + file, current_dump_folder + file)

        # Delete the temporary output folder contents
        output_files = os.listdir(tmp_output)
        for file in output_files:
            os.remove(tmp_output + file)

    # Remove tmp folder and contents
    for root, dirs, files in os.walk(tmp_folder, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(tmp_folder)

    return