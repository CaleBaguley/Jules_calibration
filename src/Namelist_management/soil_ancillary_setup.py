import src.Namelist_management.Duplicate as Duplicate
import src.Namelist_management.Edit_variable as Edit_variable

"""
Contains function to manage duplication of the soil ancillary files
"""

def duplicate_soil_ancillary(soil_ancillary_file, duplicate_address, ancillary_namelist, overwrite=False):
    """
    Duplicates the soil ancillary files to the duplicate_address
    :param soil_ancillary_file: Soil ancillary files to duplicate (str)
    :param duplicate_address: Address to copy the soil ancillary files to (str)
    :param ancillary_namelist: Namelist containing the soil ancillary file address (str)
    :param overwrite = False: If True, overwrites the files in the duplicate_address (bool)
    :return: Address of the new soil ancillary file (str)
    """

    # Duplicate the soil ancillary file
    if not Duplicate.duplicate_file(soil_ancillary_file,
                                    duplicate_address,
                                    overwrite):
        return None

    # Need to calculate the new soil ancillary file address
    new_soil_file = duplicate_address + soil_ancillary_file.split("/")[-1]

    # Update the soil ancillary file address in the ancillary namelist
    if not Edit_variable.edit_variable(ancillary_namelist,
                                       "jules_soil_props",
                                       "file",
                                       new_soil_file):
        return False

    return new_soil_file