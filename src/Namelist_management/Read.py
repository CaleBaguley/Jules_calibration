"""
Code to read a namelist file or individual namelist or namelist variable
"""

def read_file(file_address):
    """
    Reads the contents of a namelist file
    :param file_address: Address of the file (str)
    :return: Contents of the file (list)
    """

    # Open the file
    with open(file_address, "r") as file:
        lines = file.readlines()

    return lines

def read_namelist(file_address, namelist):
    """
    Reads the contents of a namelist in a namelist file
    :param file_address: Address of the file (str)
    :param namelist: Namelist to read (str)
    :return: Contents of the namelist (list)
    """

    # Open the file
    lines = read_file(file_address)

    # Find the namelist
    namelist_start_index = -1
    for i, line in enumerate(lines):
        # Check if we have reached the namelist
        if namelist in line:
            namelist_start_index = i
            break
    else:
        print("Namelist not found.")
        return []

    # Find the end of the namelist
    for i, line in enumerate(lines[namelist_start_index+1:]):
        # Check if we have reached the namelist
        if "/" == line[0]:
            namelist_end_index = namelist_start_index + i
            break
    else:
        namelist_end_index = len(lines)

    return lines[namelist_start_index:namelist_end_index]

def read_variable(file_address, namelist, variable):

    """
    Reads the value of a variable in a namelist file
    :param file_address:
    :param namelist:
    :param variable:
    :return: variable value as a string
    """

    namelist_lines = read_namelist(file_address, namelist)

    for i, line in enumerate(namelist_lines):
        # the firs entry in the line is the variable name
        if variable in line[:len(variable)]:
            # the value is the part of the line after the "=" sign
            value = line.split("=")[1].strip()

            # Some variables cover multiple lines
            for j in range(i+1, len(namelist_lines)):
                # Check if the line contains a new variable
                if '=' not in namelist_lines[j]:
                    value += namelist_lines[j].strip()
                else:
                    # Return the value without the comma at the end
                    return value[:-1]

    print("Variable not found.")
    return None


def read_soil_file(file_address):
    """
    Reads the contents of a soil file
    :param file_address: Address of the file (str)
    :return: Contents of the file (list)
    """

    # Open the file
    with open(file_address, "r") as file:
        lines = file.readlines()

    return lines

def read_soil_variable_names(ancillary_nml_address):
    """
    Reads the names of the variables in a soil ancillary file
    :param ancillary_nml_address: Address of the ancillary.nml file (str)
    :return: Names of the variables (list)
    """

    # Get the soil variable names from the soil ancillary namelist
    soil_variable_names = read_variable(ancillary_nml_address, "jules_soil_props", "var")

    # Remove the quotation marks
    soil_variable_names = soil_variable_names.replace("'", "")

    # Split the string into a list of variable names
    return soil_variable_names.split(",")

def read_soil_variable(file_address, variable, ancillary_nml_address):
    """
    Reads the value of a variable in a soil file
    :param file_address: Address of the soil ancillary file (str)
    :param variable: Variable to read (str)
    :param ancillary_nml_address: Address of the ancillary.nml file (str)
    :return: Value of the variable (str)
    """

    # Get the names of the variables in the soil file
    soil_variable_names = read_soil_variable_names(ancillary_nml_address)

    # Find the index of the variable asked for
    try:
        variable_index = soil_variable_names.index(variable)
    except ValueError:
        print("Variable not found.")
        return None

    # Open the file
    with open(file_address, "r") as file:
        lines = file.readlines()

    # Check the file only has one line
    if len(lines) != 1:
        print("Soil file should only have one line.")
        return None

    # Remove the quotation marks at the ends and split the line into a list
    line = lines[0][1:-1]
    line = line.split(" ")

    # Return the value of the variable as a string
    return line[variable_index]
