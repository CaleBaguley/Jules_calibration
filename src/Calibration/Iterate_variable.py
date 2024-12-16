"""
Code to run JULES using a series of values for a given variable
"""
import os
import datetime
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
                      overwrite_tmp_files = False,
                      append_to_run_info = False):

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
    :param overwrite_tmp_files: If True, overwrites any existing tmp files (bool) (optional)
    :param append_to_run_info: If True, appends to any existing run_info.csv file (bool) (optional)
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

    # Manage file to store run metadata
    if os.path.exists(output_folder + "run_info.csv") and append_to_run_info:

        # Check the file has the correct header
        header = "run_id,run_date," + ",".join(variable_names) + "\n"

        with open(output_folder + "run_info.csv", "r") as run_info:
            if run_info.readline() != header:
                exception("ERROR: run_info.csv file already exists but has the wrong header.")

        print("run_info.csv file already exists, appending data.")

    elif os.path.exists(output_folder + "run_info.csv") and not append_to_run_info:
        exception("ERROR: run_info.csv file already exists.\n"
                  + "Please delete the file or set append_to_run_info = True.\n")
    else:
        print("Creating run_info.csv file")
        with (open(output_folder + "run_info.csv", "w") as run_info):
            # write header
            header = "run_id,run_date"
            header += "," + ",".join(variable_names)
            header += "\n"
            run_info.write(header)

    # Iterate over the values
    for i, values in enumerate(variable_values):

        # Set the current run id
        current_run_id = run_id_prefix + f"_{datetime.datetime.now():%Y_%m_%d_%H_%M}"

        # Write the run info to the run_info.csv file
        with open(output_folder + "run_info.csv", "a") as run_info:
            run_info.write(current_run_id + "." + profile_name + ".nc,"
                           + f"{datetime.datetime.now():%Y-%m-%d %H:%M},"
                           + ",".join(values) + "\n")

        # Edit the variable
        Edit_variable.edit_variable(variable_namelist_files_full,
                                    variable_namelists,
                                    variable_names,
                                    values)



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
                          variable_names,
                          variable_namelists,
                          variable_namelist_files,
                          variable_values,
                          soil_variable_names,
                          soil_variable_values,
                          output_folder,
                          run_id_prefix,
                          keep_dump_files = False,
                          overwrite_tmp_files = False,
                          append_to_run_info = False):

    """
    Iterate over a series of values for a given soil variable
    :param jules_executable_address: file address of the JULES executable (str)
    :param master_namelist_address: folder containing the namelists to copy (str)
    :param soil_ancillary_address: soil ancillary file to use (str)
    :param variable_names: Variable to change (str)
        or list of variables to change (list of str)
        or none if no variable is to be changed (None)
    :param variable_namelists: Name of the namelist containing the changing variable (str)
        or list of namelists (list of str)
        or none if no variable is to be changed (None)
    :param variable_namelist_files: Name of the namelist file containing the changing variable (str)
        or list of namelist files (list of str)
        or none if no variable is to be changed (None)
    :param variable_values: Values of the variable to iterate over as a 1D list of strings (list of strings)
        or lait of lists containing each set of variable values to try (list of lists of str)
        or none if no variable is to be changed (None)
    :param soil_variable_name: soil variable to iterate over (str)
        or list of soil variables to iterate over (list of str)
        or none if no soil variable is to be changed (None)
    :param soil_variable_values: soil variable values to iterate over (list of str)
        or list of lists of soil variable values to iterate over (list of lists of str)
        or none if no soil variable is to be changed (None)
    :param output_folder: JULES output folder (str)
    :param run_id_prefix: Prefix for all run ids (str)
    :param keep_dump_files: save JULES dumpfiles (bool)
    :param overwrite_tmp_files: overwrite any existing tmp files (bool)
    :param append_to_run_info: append to any existing run_info.csv file (bool)
    :return:
    """

    # Check there are variables to iterate over
    if variable_values is None and soil_variable_values is None:
        exception("ERROR: No variables to iterate over.\n")

    # Manage JULES variables input options
    # If no variable is to be changed, set the variables to empty lists
    if variable_names is None:
        variable_names = []
        variable_namelists = []
        variable_namelist_files = []
        variable_values = []
    # If only one variable is to be changed, set the variables to lists
    elif type(variable_names) is str:
        variable_names = [variable_names]
        variable_namelists = [variable_namelists]
        variable_namelist_files = [variable_namelist_files]
        variable_values = [variable_values]

    # Manage soil variables input options
    # If no soil variable is to be changed, set the variables to empty lists
    if soil_variable_names is None:
        soil_variable_names = []
        soil_variable_values = []
    # If only one soil variable is to be changed, set the variables to lists
    elif type(soil_variable_names) is str:
        soil_variable_names = [soil_variable_names]
        soil_variable_values = [soil_variable_values]

    # Check the number of iterations is the same for both variables
    if len(variable_values) != len(soil_variable_values) and len(variable_values) > 0 and len(soil_variable_values) > 0:
        exception("ERROR: The number of iterations for the JULES variables and soil variables must be the same.\n")

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

    # Manage file to store run metadata
    if os.path.exists(output_folder + "run_info.csv") and append_to_run_info:

        # Check the file has the correct header
        header = "run_id,run_date"
        if len(variable_names) > 0:
            header += "," + ",".join(variable_names)
        if len(soil_variable_names) > 0:
            header += "," + ",".join(soil_variable_names)
        header += "\n"

        with open(output_folder + "run_info.csv", "r") as run_info:
            if run_info.readline() != header:
                exception("ERROR: run_info.csv file already exists but has the wrong header.\n")

        print("run_info.csv file already exists, appending data.")

    elif os.path.exists(output_folder + "run_info.csv") and not append_to_run_info:
        exception("ERROR: run_info.csv file already exists.\n"
                  + "Please delete the file or set append_to_run_info = True.\n")
    else:
        print("Creating run_info.csv file")
        with (open(output_folder + "run_info.csv", "w") as run_info):
            # write header
            header = "run_id,run_date"
            if len(variable_names) > 0:
                header += "," + ",".join(variable_names)
            if len(soil_variable_names) > 0:
                header += "," + ",".join(soil_variable_names)
            header += "\n"
            run_info.write(header)

    # Set up variables to hold the current variable values
    current_JULES_variable_values = []
    current_soil_variable_values = []

    # Calculate the number of iterations
    n_iterations = max(len(variable_values), len(soil_variable_values))

    # Iterate over the values
    for i in range(n_iterations):

        # Set the current run id
        current_run_id = run_id_prefix + f"_{datetime.datetime.now():%Y_%m_%d+%H_%M}"

        print(f"-- Running iteration {i} with run_id {current_run_id} --")

        # Get the variable values for the current iteration
        if(len(variable_values) > 0):
            current_JULES_variable_values = variable_values[i]
        if(len(soil_variable_values) > 0):
            current_soil_variable_values = soil_variable_values[i]

        # Write the run info to the run_info.csv file
        with open(output_folder + "run_info.csv", "a") as run_info:
            out_string = current_run_id + "." + profile_name + ".nc," + f"{datetime.datetime.now():%Y-%m-%d %H:%M}"
            if len(variable_names) > 0:
                out_string += "," + ",".join(current_JULES_variable_values)
            if len(soil_variable_names) > 0:
                out_string += "," + ",".join(current_soil_variable_values)
            out_string += "\n"
            run_info.write(out_string)

        # Edit JULES variables
        Edit_variable.edit_variable(variable_namelist_files,
                                    variable_namelists,
                                    variable_names,
                                    current_JULES_variable_values)

        # Edit soil variables
        Edit_variable.edit_soil_variable(tmp_soil_file,
                                         soil_variable_names,
                                         current_soil_variable_values,
                                         tmp_namelist + "ancillaries.nml")

        # Set the current run id
        current_run_id = run_id_prefix + f"_{i}"

        # Edit the output file name
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