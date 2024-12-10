
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
            lines[namelist_start_index+1 + i] = variable + " = " + value + "\n"
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
