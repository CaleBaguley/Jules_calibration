"""
Code to optimise a variable in a namelist file using observational data
"""
import pandas as pd

from Calibration.Calibration.setup_calibration_files import setup_tmp_folders
from Calibration.general.file_management import make_folder, delete_folder
from Calibration.Namelist_management.Read import read_variable
from Calibration.Namelist_management.Outpur_nml_management import is_in_output
from Calibration.Namelist_management.Edit_variable import edit_variable
from Calibration.Run_JULES.Run_JULES import run_JULES

from xarray import open_dataset
from pandas import merge
from logging import exception
from sklearn.metrics import mean_squared_error
from scipy.optimize import minimize
import os
from datetime import datetime


def optimise_variable(jules_executable_address,
                      master_namelist_address,
                      variable_names,
                      variable_namelists,
                      variable_namelist_files,
                      observation_data,
                      observational_variable_keys,
                      jules_out_variable_keys,
                      run_id_prefix,
                      max_iter = 100,
                      variable_initial_values = None,
                      variable_bounds = None,
                      obs_variable_weights = None,
                      output_folder = None,
                      keep_dump_files = False,
                      tmp_folder = None,
                      overwrite_tmp_files = False,
                      overwrite_output_files = False,
                      append_to_run_info = False,
                      save_rmse = False,
                      save_run_time = False,
                      minimize_method = "Nelder-Mead",
                      verbose = False):

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
    :param observational_variable_keys: Keys of the variables in the observation data file used to assess model
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

    if verbose:
        print("Setting up runs...")

    # Manage the case where the user only wants to iterate over one variable
    if type(variable_names) is str:
        variable_names = [variable_names]
        variable_namelists = [variable_namelists]
        variable_namelist_files = [variable_namelist_files]

    # Check the variable info is the same length
    if len(variable_names) != len(variable_namelists) or len(variable_names) != len(variable_namelist_files):
        exception("ERROR: variable_names, variable_namelists and variable_namelist_files must be the same length.")

    # Manage the case where the user only wants to iterate over one observation variable and JULES output variable
    if(type(observational_variable_keys) is str):
        observational_variable_keys = [observational_variable_keys]
    if(type(jules_out_variable_keys) is str):
        jules_out_variable_keys = [jules_out_variable_keys]

    # Check the observation variables and JULES output variables are the same length
    if len(observational_variable_keys) != len(jules_out_variable_keys):
        exception("ERROR: obs_variable_keys and jules_out_variable_keys must be the same length.")

    # Set up the temporary folders
    print("Setting up temp folder")
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

            # convert to float
            if('*' in variable_initial_values[-1]):
                variable_initial_values[-1] = float(variable_initial_values[-1].split('*')[1])
            else:
                variable_initial_values[-1] = float(variable_initial_values[-1].split(",")[0])

    print(f"Initial values:")
    for i, name in enumerate(variable_names):
        print(f"{name} = {variable_initial_values[i]}")

    # Setup output folder
    if output_folder is not None:
        output_folder = make_folder(output_folder, overwrite_existing=overwrite_output_files)

    # Create the run_info.csv file
    run_info_address = output_folder + run_id_prefix + "_run_info.csv"
    if not append_to_run_info:
        if(os.path.isfile(run_info_address)):
            os.remove(run_info_address)

        with open(run_info_address, "w") as run_info:
            run_info.write("run_id, run_date, " + ", ".join(variable_names))

            if save_rmse:
                if len(observational_variable_keys) > 1:
                    for key in observational_variable_keys:
                        run_info.write(", " + key)
                run_info.write(", rmse")
            if save_run_time:
                run_info.write(", run_time")

            run_info.write("\n")


    # Get the output profile name
    profile_name = read_variable(tmp_folder + "namelist/output.nml",
                                 "jules_output_profile",
                                 "profile_name")

    # Remove any quotes from the profile name
    profile_name = profile_name.strip("'")
    profile_name = profile_name.strip('"')

    # Change the output directory in the namelist file
    edit_variable(tmp_folder + "namelist/output.nml",
                  "jules_output",
                  "output_dir",
                  "'" + tmp_folder + "output/" + "'")

    # setup variable keys
    if type(observational_variable_keys) is str:
        observational_variable_keys = [observational_variable_keys]

    if type(jules_out_variable_keys) is str:
        jules_out_variable_keys = [jules_out_variable_keys]

    # Check the jules_out_variable_keys are in the output namelist
    if not is_in_output(jules_out_variable_keys, tmp_folder + "namelist/output.nml"):
        exception("ERROR: One or more of jules_out_variable_keys ("
                  + str(jules_out_variable_keys)
                  + ") are not in the output namelist.")

    # Read in observation data and reduce to the required variables
    observation_data = observation_data[observational_variable_keys]

    # -- Optimisation --------------------------------------------------------------------------
    if verbose:
        print("Optimising variables...")
    current_run_id = run_id_prefix + "_0"
    minimize(calc_rmse_for_given_values,
             x0 = variable_initial_values,
             args = (variable_names,
                     variable_namelists,
                     variable_namelist_files_full,
                     tmp_folder,
                     jules_executable_address,
                     output_folder,
                     [current_run_id],
                     profile_name,
                     observation_data,
                     observational_variable_keys,
                     jules_out_variable_keys,
                     run_info_address,
                     save_rmse,
                     save_run_time,
                     obs_variable_weights,
                     verbose),
             bounds = variable_bounds,
             method = minimize_method,
             options= {"max_iter": max_iter}
             )

    if verbose:
        print("Optimisation complete.")
    # -- Clean up ------------------------------------------------------------------------------
    # Remove the temporary folders
    delete_folder(tmp_folder)

def calc_rmse_for_given_values(variable_values,
                               variable_names,
                               variable_namelists,
                               variable_namelist_files,
                               tmp_folder,
                               jules_executable_address,
                               output_folder,
                               current_run_id,
                               profile_name,
                               observational_data,
                               observational_variable_keys,
                               jules_out_variable_keys,
                               run_info_out_address,
                               save_rmse = False,
                               save_run_time = False,
                               obs_variable_weights = None,
                               verbose = False):
    """
    Function used in minimisation to calculate the RMSE for a given set of variable values
    :param variable_values:
    :return:
    """

    current_run_id[0] = "_".join(current_run_id[0].split("_")[:-1]) + "_" + str(int(current_run_id[0].split("_")[-1]) + 1)

    if verbose:
        print(f"Setup {current_run_id[0]}...")

    # Setup rmse output if needed
    if save_rmse:
        rmse_out_address = run_info_out_address
    else:
        rmse_out_address = None

    # Set the variable values in the namelist files
    # TODO: fix this hard coded 5
    variable_values_string = [f"5*{val}" for val in variable_values]
    edit_variable(variable_namelist_files,
                  variable_namelists,
                  variable_names,
                  variable_values_string)

    # Write the run info to the run_info.csv file
    if output_folder is not None:
        with open(run_info_out_address, "a") as run_info:
            run_info.write(current_run_id[0] + "." + profile_name + ".nc,"
                           + f"{datetime.now():%Y-%m-%d %H:%M},"
                           + ",".join([str(val) for val in variable_values]))

            run_info.close()

    # Update the run id

    edit_variable(tmp_folder + "namelist/output.nml",
                  'jules_output',
                  'run_id',
                  "'" + current_run_id[0] + "'")

    # Run JULES
    if verbose:
        print(f"Running {current_run_id[0]}...")
    run_time = datetime.now()
    run_JULES(jules_executable_address,
              tmp_folder + "namelist/",
              terminal_output_address = tmp_folder + "output/" + current_run_id[0] + "." + profile_name + ".out")
    run_time = datetime.now() - run_time

    # calculate RMSE
    if verbose:
        print(f"Cacluate RMSE for {current_run_id[0]}...")
    JULES_data = open_dataset(tmp_folder + "output/" + current_run_id[0] + "." + profile_name + ".nc")
    JULES_data = JULES_data[['time'] + jules_out_variable_keys]
    JULES_data = JULES_data.squeeze(dim=["x", "y"], drop=True)
    JULES_data = JULES_data.to_pandas()
    JULES_data.index = pd.to_datetime(JULES_data.index)

    rmse = compare_to_obs(observational_data,
                          JULES_data,
                          observational_variable_keys,
                          jules_out_variable_keys,
                          obs_variable_weights = obs_variable_weights,
                          rmse_out_address = rmse_out_address,
                          verbose = verbose)

    if verbose:
        print(f"Cleening up {current_run_id[0]}...")
    # Save run time
    if save_run_time and output_folder is not None:
        with open(run_info_out_address, "a") as run_info:
            run_info.write(f",{run_time.total_seconds()}")
            run_info.close()

    # End run entry in run_info.csv
    if output_folder is not None:
        with open(run_info_out_address, "a") as run_info:
            run_info.write("\n")
            run_info.close()

    # clean tmp_output
    for file in os.listdir(tmp_folder + "output/"):
        os.remove(tmp_folder + "output/" + file)

    return rmse


def compare_to_obs(obs_data,
                   JULES_output,
                   obs_variable_keys,
                   jules_out_variable_keys,
                   time_period = None,
                   obs_variable_weights = None,
                   rmse_out_address = None,
                   verbose = False):
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
        print("Observation data:")
        print(obs_data)
        print("JULES output:")
        print(JULES_output)
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
                                              merged_data[jules_key]))

        mean_rmse += rmse_values[i] * obs_variable_weights[i]

    # Save the RMSE values to the end of the output file
    if rmse_out_address is not None:
        if verbose:
            print(f"Saving RMSE values to {rmse_out_address}...")
        with open(rmse_out_address, "a") as file:
            if len(obs_variable_keys) > 1:
                file.write(", ".join(obs_variable_keys))

            file.write(f", {mean_rmse}")
            file.close()

    return mean_rmse