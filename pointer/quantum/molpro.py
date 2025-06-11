"""Submit and analyze data from Molpro calculations."""


################################################################################
def process_ionization(filename: str) -> (float, float):
    """
    Parse a Molpro output file to extract IP and HOMO data.

    Parameters
    ----------
    filename : str
        Name of output file containing results of the ionization potential
        calculation.

    Returns
    -------
    ip : float
        Ionization Potential in a.u.
    homo : float
        HOMO (highest occupied Molecular Orbital) in a.u.
    """

    # POInter convention is to have Molpro store the ionization energy as a
    # variable E_IONIZATION:
    #       SETTING E_IONIZATION   =         0.46602931  AU
    IONIZATION_FLAG = "SETTING E_IONIZATION"
    # Molpro stores HOMO information internally. The HOMO in a.u. units is the
    # 3rd column. We are only interested in the HOMO for the atom, hence we
    # only want the first instance of the flag.
    #       HOMO      5.1    -0.899654 =     -24.4808eV
    HOMO_FLAG = "HOMO     "

    with open(filename, "r") as f:
        data = f.readlines()

    got_ip = False
    got_homo = False
    for line in data:
        if got_ip and got_homo:
            break
        elif IONIZATION_FLAG in line:
            ip = float(line.split()[-2])
            got_ip = True
        elif HOMO_FLAG in line and got_homo == False:
            homo = float(line.split()[2])
            got_homo = True
        else:
            continue
    else:
        raise ValueError("Error in Molpro file, does not contain HOMO and IP data.")

    return ip, homo


################################################################################

if __name__ == "__main__":
    import sys

    process_ionization(sys.argv[1])
