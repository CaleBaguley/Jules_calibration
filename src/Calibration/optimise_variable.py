"""
Code to optimise a variable in a namelist file using observational data
"""

from src.Calibration.setup_calibration_files import setup_tmp_folders
from src.general.file_management import make_folder
from src.Namelist_management.Read import read_variable
from src.Namelist_management.Outpur_nml_management import is_in_output

from xarray import open_dataset
from logging import exception


def optimise_variable(jules_executable_address,
                      master_namelist_address,
                      variable_names,
                      variable_namelists,
                      variable_namelist_files,
                      observation_data_address,
                      obs_variable_keys,
                      jules_out_variable_keys,
                      run_id_prefix,
                      variable_limits = None,
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

    # Set up the temporary folders
    tmp_folder = setup_tmp_folders(master_namelist_address,
                                   tmp_folder,
                                   overwrite_tmp_files)

    variable_namelist_files_full = [tmp_folder + "namelist/" + file for file in variable_namelist_files]

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

    # Read in observation data
    obs_data = open_dataset(observation_data_address)

    # -- Optimisation --------------------------------------------------------------------------


