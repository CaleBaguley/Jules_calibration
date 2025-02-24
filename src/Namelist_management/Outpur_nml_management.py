"""
Contains functions used to manage the output namelist files
"""

from src.Namelist_management.Read import read_file
from logging import exception

def is_in_output(variable, output_namelist_file):
    """
    Checks if a variable is in the output namelist
    :param variable: Variable to check (str)
                     or list of variables to check (list of str)
    :param output_namelist_file: File address of the output namelist (str)
    :return: True if the variable is in the output namelist, False otherwise
    """

    # Read the output namelist file
    namelist_contents = read_file(output_namelist_file)

    # Loop through the lines to reach the output variable names
    line_num = 0
    for line_num, line in enumerate(namelist_contents):
        if "var_name=" in line:
            break
    else:
        exception("ERROR: Output variable names not found in the output namelist file.\n")

    # loop over each variable to check
    for var in variable:
        # Loop over the lines to check if the variable is in the output namelist
        for line in namelist_contents[line_num:]:

            # If the first entry is not ' then the list of variables has ended
            if "'" != line[0]:
                return False

            # Check if the variable is in the line
            elif var in line:
                break

        # If the variable was not found
        else:
            return False

    return True
