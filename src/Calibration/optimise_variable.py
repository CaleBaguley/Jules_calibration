"""
Code to optimise a variable in a namelist file using observational data
"""

from src.Calibration.setup_calibration_files import setup_tmp_folders
from src.general.file_management import make_folder
from src.Namelist_management.Read import read_variable
from src.Namelist_management.Outpur_nml_management import is_in_output
from src.Namelist_management.Edit_variable import edit_variable

from xarray import open_dataset
from pandas import read_csv, merge
from logging import exception
from copy import copy
from sklearn.metrics import mean_squared_error


def optimise_variable(jules_executable_address,
                      master_namelist_address,
                      variable_names,
                      variable_namelists,
                      variable_namelist_files,
                      observation_data_address,
                      obs_variable_keys,
                      jules_out_variable_keys,
                      run_id_prefix,
                      variable_initial_values = None,
                      variable_limits = None,
                      obs_variable_weights = None,
                      output_folder = None,
                      keep_dump_files = False,
                      tmp_folder = None,
                      overwrite_tmp_files = False,
                      append_to_run_info = False):

    """
    Optimises a variable in a namelist file using observational data
    :param jules_executable_address: Address of the JULES executable (str)
    :param master_namelist_address: Address of the master namelist file (str)
    :param variable_names: Name of the variable to optimise (str) or list of variables to optimise (list of str)
    :param variable_namelists: Name of the namelist to optimise the variable in (str)
                               or list of namelists to optimise the variable in (list of str)
    :param variable_namelist_files: Name of the namelist file to optimise the variable in (str)
                                    or list of namelist files to optimise the variable in (list of str)
    :param observation_data_address: Address of the observation data file (str)
    :param obs_variable_keys: Keys of the variables in the observation data file used to assess model
                              (str or list of str)
    :param jules_out_variable_keys: Keys of the variables in the JULES output file used to assess model
                                    (srt or list of str)
    :param run_id_prefix: Prefix to add to the run id (str)
    :param variable_limits: Limits of the variable to optimise (list of tuples) (optional)
    :param output_folder: Address to save run output (str) (optional)
    :param keep_dump_files: If True, keeps the dump files (bool) (optional)
    :param overwrite_tmp_files: If True, overwrites existing temporary files (bool) (optional)
    :param append_to_run_info: If True, appends the run info to the run_info file (bool) (optional)
    :return:
    """

    # -- Setup ---------------------------------------------------------------------------------

    # Manage the case where the user only wants to iterate over one variable
    if type(variable_names) is str:
        variable_names = [variable_names]
        variable_namelists = [variable_namelists]
        variable_namelist_files = [variable_namelist_files]

    # Check the variable info is the same length
    if len(variable_names) != len(variable_namelists) or len(variable_names) != len(variable_namelist_files):
        exception("ERROR: variable_names, variable_namelists and variable_namelist_files must be the same length.")

    # Manage the case where the user only wants to iterate over one observation variable and JULES output variable
    if(type(obs_variable_keys) is str):
        obs_variable_keys = [obs_variable_keys]
    if(type(jules_out_variable_keys) is str):
        jules_out_variable_keys = [jules_out_variable_keys]

    # Check the observation variables and JULES output variables are the same length
    if len(obs_variable_keys) != len(jules_out_variable_keys):
        exception("ERROR: obs_variable_keys and jules_out_variable_keys must be the same length.")

    # Set up the temporary folders
    tmp_folder = setup_tmp_folders(master_namelist_address,
                                   tmp_folder,
                                   overwrite_tmp_files)

    # Create list of the full file addresses for the variable namelist files
    variable_namelist_files_full = [tmp_folder + "namelist/" + file for file in variable_namelist_files]

    # Set the initial values of the variables
    if variable_initial_values is not None:
        for i, val in enumerate(variable_initial_values):
            edit_variable(variable_namelist_files_full[i],
                          variable_namelists[i],
                          variable_names[i],
                          val)
    # Read the initial values of the variables if not provided
    else:
        variable_initial_values = []
        for i, name in enumerate(variable_names):
            variable_initial_values.append(read_variable(variable_namelist_files_full[i],
                                                         variable_namelists[i],
                                                         variable_names[i]))

    print(f"Initial values:")
    for i, name in enumerate(variable_names):
        print(f"{name} = {variable_initial_values[i]}")

    # Set up variable to hold the current values when iterating
    current_variable_values = copy(variable_initial_values)

    # Setup output folder
    if output_folder is not None:
        output_folder = make_folder(output_folder, overwrite_existing=False)

    # Get the output profile name
    profile_name = read_variable(tmp_folder + "namelist/output.nml",
                                 "jules_output_profile",
                                 "profile_name")

    # Remove any quotes from the profile name
    profile_name = profile_name.strip("'")
    profile_name = profile_name.strip('"')

    # setup variable keys
    if type(obs_variable_keys) is str:
        obs_variable_keys = [obs_variable_keys]

    if type(jules_out_variable_keys) is str:
        jules_out_variable_keys = [jules_out_variable_keys]

    # Check the jules_out_variable_keys are in the output namelist
    if not is_in_output(jules_out_variable_keys, tmp_folder + "namelist/output.nml"):
        exception("ERROR: One or more of jules_out_variable_keys ("
                  + str(jules_out_variable_keys)
                  + ") are not in the output namelist.")

    # Read in observation data and reduce to the required variables
    obs_data = read_csv(observation_data_address)
    obs_data = obs_data[obs_variable_keys]

    # -- Optimisation --------------------------------------------------------------------------


def compare_to_obs(obs_data,
                   JULES_output,
                   obs_variable_keys,
                   jules_out_variable_keys,
                   time_period = None,
                   obs_variable_weights = None,
                   rmse_out_address = None):
    """
    Compares the JULES output to the observational data
    :param obs_data: pandas dataframe of the observational data
    :param JULES_output: pandas dataframe of the JULES output
    :param obs_variable_keys: Keys of the variables in the observation data file used to assess model
                              (str or list of str)
    :param jules_out_variable_keys: Keys of the variables in the JULES output file used to assess model
                                    (srt or list of str)
    :param time_period: Period to compare the data over (pandas datetime) (optional)
    :param obs_variable_weights: Weights to apply to the variables in the observation data (list of float) (optional)
    :param rmse_out_address: Address to save the RMSE outputs (str) (optional)
    :return:
    """

    # Merge the dataframes on the time index
    merged_data = merge(obs_data, JULES_output, how = 'inner', left_index=True, right_index=True)

    if len(merged_data) == 0:
        exception("ERROR: Observation and JULES output don't match.")
        exit()

    # Reduce the data to the time period
    if time_period is not None:
        merged_data = merged_data[time_period[0]:time_period[1]]

    if(obs_variable_weights is None):
        obs_variable_weights = [1] * len(obs_variable_keys)

    # Normalise the weights
    total_weight = sum(obs_variable_weights)
    obs_variable_weights = [w / total_weight for w in obs_variable_weights]

    # Calculate the RMSE for each variable
    rmse_values = []
    mean_rmse = 0
    for i, obs_key in enumerate(obs_variable_keys):
        jules_key = jules_out_variable_keys[i]

        # Calculate the rmse
        rmse_values.append(mean_squared_error(merged_data[obs_key],
                                              merged_data[jules_key],
                                              squared=False))

        mean_rmse += rmse_values[i] * obs_variable_weights[i]

    # Save the RMSE values to the end of the output file
    if rmse_out_address is not None:
        with open(rmse_out_address, "w") as file:
            file.write(", ".join(obs_variable_keys) + f", {mean_rmse}")

    return mean_rmse