import os

"""
Contains code used to duplicate the contents of a folder containing namelist files
"""

def duplicate(namelist_folder, duplicate_address, overwrite=False):
    """
    Creates a coppy of the namelist files in the duplicate_address.
    NOTE: Only copies files ending in nml.
    :param namelist_folder: Namelist to copy (str)
    :param duplicate_address: Address to copy the namelists to (str)
    :param overwrite = False: If True, overwrites the files in the duplicate_address (bool)
    :return: True if the files were copied, False otherwise
    """

    if not os.path.exists(duplicate_address):
        print("Creating directory: ", duplicate_address)
        os.makedirs(duplicate_address)

    # Already contains files?
    if os.listdir(duplicate_address) and not overwrite:
        print("Directory already contains files. Use overite = True to overwrite.")
        return False

    # Copy files
    print("Copying files...")
    for file in os.listdir(namelist_folder):
        if file.endswith(".nml"):
            print("Copying file: ", file)

            # Need to replace spaces with "\ " for the terminal to understand the path
            file_to_copy = (namelist_folder + file).replace(" ", "\ ")
            duplicate_address_terminal = duplicate_address.replace(" ", "\ ")

            # Copy the file using cp terminal command
            os.system("cp " + file_to_copy + " " + duplicate_address_terminal)

    return True

def duplicate_file(file_address, duplicate_address, overwrite=False):
    """
    Creates a copy of the file in the duplicate_address.
    :param file_address: File to copy (str)
    :param duplicate_address: Address to copy the file to (str)
    :param overwrite = False: If True, overwrites the file in the duplicate_address (bool)
    :return: True if the file was copied, False otherwise
    """

    if not os.path.exists(duplicate_address):
        print("Creating directory: ", duplicate_address)
        os.makedirs(duplicate_address)

    if not overwrite:
        new_address = duplicate_address + file_address.split("/")[-1]
        if os.path.exists(new_address):
            print("File already exists. Use overwrite = True to overwrite.")
            return False

    # Need to replace spaces with "\ " for the terminal to understand the path
    file_to_copy = file_address.replace(" ", "\ ")
    duplicate_address_terminal = duplicate_address.replace(" ", "\ ")

    # Copy the file using cp terminal command
    os.system("cp " + file_to_copy + " " + duplicate_address_terminal)

    return True