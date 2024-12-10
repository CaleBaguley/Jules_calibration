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
        # Check if we have reached the next namelist
        if "&" == line[0]:
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

    for line in namelist_lines:
        if variable in line:
            return line.split("=")[1].strip()[:-1]
    else:
        print("Variable not found.")
        return None