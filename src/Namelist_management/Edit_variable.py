import src.Namelist_management.Read as Read
"""
Code to open a namelist file and edit a single input variable
"""

def edit_variable(file_address, namelist, variable, value):
    """
    Edits the value of a variable in a namelist file
    :param file_address: Address of the file (str)
    :param namelist: Namelist to edit (str)
    :param variable: Variable to edit (str)
    :param value: Value to set the variable to (str)
    :return: True if the variable was edited, False otherwise
    """

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
        print("Namelist not found.")
        return False

    # Find the variable
    for i, line in enumerate(lines[namelist_start_index+1:]):
        # Check if we have reached the next namelist
        if "&" == line[0]:
            print("Variable not found.")
            return False
        # Check if the variable is in the line
        elif variable in line:
            print("Variable found.")
            lines[namelist_start_index+1 + i] = variable + "=" + value + ",\n"
            break
    # If the variable was not found
    else:
        print("Variable not found.")
        return False

    # Write the changes to the file
    print("Writing changes to file...")
    with open(file_address, "w") as file:
        file.writelines(lines)

    return True

def edit_soil_variable(file_address, variable, new_value, ancillary_file):
    """
    Edits the value of a variable in a soil file
    :param file_address: Address of the file (str)
    :param variable: Variable to edit (str)
    :param new_value: Value to set the variable to (str)
    :return: True if the variable was edited, False otherwise
    """

    # Get the soil variable names
    soil_variables = Read.read_soil_variable_names(ancillary_file)

    # Check if the variable is in the soil file
    if variable not in soil_variables:
        print("Variable not found.")
        return False

    # Get the position of the variable to change
    variable_index = soil_variables.index(variable)

    # Get the soil variables
    soil_values = Read.read_soil_variable_values(file_address)

    # Change the value
    soil_values[variable_index] = new_value

    # Write the changes to the file
    write_soil_variables(file_address, soil_values)

    return True

def write_soil_variables(file_address, soil_values):
    """
    Writes all the soil variables to a soil file
    :param file_address: Address of the file (str)
    :param soil_values: Values of the soil variables (list)
    :return: True if the variables were written, False otherwise
    """

    # Convert the list of values to a string
    string = " ".join(soil_values)

    # Write the changes to the file
    print("Writing changes to file...")
    with open(file_address, "w") as file:
        file.write(string)

    return True