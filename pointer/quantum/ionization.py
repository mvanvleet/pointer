"""Calculate and analyze ionization potentials."""

from . import molpro


################################################################################
def submit_ip(package="molpro"):
    """
    Placeholder function to show example docstring (NumPy format).

    Replace this function and doc string for your own project.

    Parameters
    ----------
    with_attribution : bool, Optional, default: True
        Set whether or not to display who the quote is from.

    Returns
    -------
    quote : str
        Compiled string including quote and optional attribution.
    """

    if package != "molpro":
        return NotImplementedError

    return NotImplementedError


################################################################################


################################################################################
def process_output(filename: str, package="molpro") -> (float, float):
    """
    Parse an output file to extract IP and HOMO data.

    Parameters
    ----------
    filename : str
        Name of output file containing results of the ionization potential
        calculation.
    package : str, Optional, default: "molpro"
        Software package used in the calculation. Currently only Molpro is
        supported.

    Returns
    -------
    ip : float
        Ionization Potential in a.u.
    homo : float
        HOMO (highest occupied Molecular Orbital) in a.u.
    """

    if package != "molpro":
        return NotImplementedError
    else:
        ip, homo = molpro.process_ionization(filename)

    return ip, homo


################################################################################


if __name__ == "__main__":
    import sys

    print("IP, HOMO")
    print(process_output(sys.argv[1], package="molpro"))
