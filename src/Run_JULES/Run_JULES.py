import os

"""
Code to run JULES from python
"""

def run_JULES(jules_executable_address, namelist_folder_address):
    """
    Run JULES from python
    :param jules_executable_address: Address of JULES executable
    :param namelist_folder_address: Address of the folder containing the namelists
    """

    # Get the current working directory
    cwd = os.getcwd()

    # cd to the namelist folder
    os.chdir(namelist_folder_address)

    # Run JULES
    os.system(jules_executable_address)

    # cd back to the original directory
    os.chdir(cwd)
