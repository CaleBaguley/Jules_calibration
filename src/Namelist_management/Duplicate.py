import os

from src.Namelist_management import Edit_variable as Edit_variable

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


def duplicate_soil_ancillary(soil_ancillary_file, duplicate_address, ancillary_namelist_file, overwrite=False):
    """
    Duplicates the soil ancillary files to the duplicate_address
    :param soil_ancillary_file: Soil ancillary files to duplicate (str)
    :param duplicate_address: Address to copy the soil ancillary files to (str)
    :param ancillary_namelist_file: Address of the ancillary namelist file (str)
    :param overwrite = False: If True, overwrites the files in the duplicate_address (bool)
    :return: Address of the new soil ancillary file (str)
    """

    # Duplicate the soil ancillary file
    if not duplicate_file(soil_ancillary_file,
                          duplicate_address,
                          overwrite):
        return None

    # Need to calculate the new soil ancillary file address
    new_soil_file = duplicate_address + soil_ancillary_file.split("/")[-1]

    # Update the soil ancillary file address in the ancillary namelist
    if not Edit_variable.edit_variable(ancillary_namelist_file,
                                       "jules_soil_props",
                                       "file",
                                       "'" + new_soil_file + "'"):
        return False

    return new_soil_file
