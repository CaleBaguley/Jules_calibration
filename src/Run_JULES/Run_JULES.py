import os
import subprocess

"""
Code to run JULES from python
"""

def run_JULES(jules_executable_address, namelist_folder_address, terminal_output_address=None):
    """
    Run JULES from python
    :param jules_executable_address: Address of JULES executable (str)
    :param namelist_folder_address: Address of the folder containing the namelists (str)
    :param terminal_output_address: Address of the file to write the terminal output to (str) (optional)
    """

    # Get the current working directory
    cwd = os.getcwd()

    # cd to the namelist folder
    os.chdir(namelist_folder_address)

    # Run JULES
    if(terminal_output_address is not None):
        with open(terminal_output_address, "w") as f:
            subprocess.run(jules_executable_address, stdout=f)
    else:
        os.system(jules_executable_address)

    # cd back to the original directory
    os.chdir(cwd)
