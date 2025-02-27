import Calibration.Namelist_management.Read as Read
"""
Code to open a namelist file and edit a single input variable
"""

def edit_variable(file_address, namelist, variable, value, verbose = False):
    """
    Edits the value of a variable in a namelist file
    :param file_address: Address of the file (str) or list of addresses (list of str)
    :param namelist: Namelist to edit (str) or list of namelists to edit (list of str)
    :param variable: Variable to edit (str) or list of variables to edit (list of str)
    :param value: Value to set the variable to (str) or list of values to set the variables to (list of str)
    :param verbose = False: If True, prints the changes made (bool)
    :return: True if the variable was edited, False otherwise
    """

    # If multiple variables are to be edited
    if type(file_address) == list:
        for i in range(len(file_address)):
            if not edit_variable(file_address[i], namelist[i], variable[i], value[i]):
                return False
        return True

    # Open the file
    with open(file_address, "r") as file:
        lines = file.readlines()

    # Find the namelist
    namelist_start_index = -1
    for i, line in enumerate(lines):
        # Check if we have reached the namelist
        if namelist in line:
            namelist_start_index = i
            break
    else:
        print(f"Namelist ({namelist}) not found.")
        return False

    # Find the variable
    for i, line in enumerate(lines[namelist_start_index+1:]):
        # Check if we have reached the next namelist
        if "&" == line[0]:
            print(f"Variable ({variable}) not found.")
            return False
        # Check if the variable is in the line
        elif variable in line:
            print(f"Variable ({variable}) found.")
            lines[namelist_start_index+1 + i] = variable + "=" + value
            break
    # If the variable was not found
    else:
        print(f"Variable ({variable}) not found.")
        return False

    # Need to account for the case where the variable is the last in the namelist
    if lines[namelist_start_index+1 + i + 1] == "/\n":
        lines[namelist_start_index+1 + i] += "\n"
    else:
        lines[namelist_start_index+1 + i] += ",\n"

    # Write the changes to the file
    if verbose:
        print("Writing changes to file...")
    with open(file_address, "w") as file:
        file.writelines(lines)

    return True

def edit_soil_variable(file_address, variables, new_values, ancillary_file, verbose = False):
    """
    Edits the value of a variable in a soil file
    :param file_address: Address of the file (str)
    :param variables: Variable to edit (str) or list of variables to edit (list of str)
    :param new_value: Value to set the variable to (str) or list of values to set the variables to (list of str)
    :param ancillary_file: Address of the ancillary file (str)
    :param verbose = False: If True, prints the changes made (bool)
    :return: True if the variable was edited, False otherwise
    """

    # If the variable is a string convert to a list
    if type(variables) == str:
        variables = [variables]
        new_values = [new_values]

    # Get all the soil variable names
    soil_variables = Read.read_soil_variable_names(ancillary_file)

    # Check if each variable is in the soil file
    for variable in variables:
        if variable not in soil_variables:
            print(f"Variable, {variable}, not found in {ancillary_file}, $jules_soil_props.")
            return False

    # Get the position of the variable to change
    variable_indecies = []
    for variable in variables:
        variable_indecies.append(soil_variables.index(variable))

    # Get the values soil variables
    soil_values = Read.read_soil_variable_values(file_address)

    # Change the values
    for i in range(len(variable_indecies)):
        soil_values[variable_indecies[i]] = new_values[i]

    # Write the changes to the file
    write_soil_variables(file_address, soil_values, verbose)

    return True

def write_soil_variables(file_address, soil_values, verbose = False):
    """
    Writes all the soil variables to a soil file
    :param file_address: Address of the file (str)
    :param soil_values: Values of the soil variables (list)
    :param verbose = False: If True, prints the changes made (bool)
    :return: True if the variables were written, False otherwise
    """

    # Convert the list of values to a string
    string = " ".join(soil_values)

    # Write the changes to the file
    if(verbose):
        print("Writing changes to file...")
    with open(file_address, "w") as file:
        file.write(string)

    return True