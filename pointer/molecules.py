"""Define monomer and dimer objects."""

import numpy as np
from pathlib import Path


################################################################################
class Monomer:
    """Parses information about a single molecule from a .xyz file (or alternately a
    list of elements and an xyz array), and constructs an object containing the
    molecule's name, atoms, and (optionally) conformers."""

    ############################################################################
    def __init__(self, xyzfile="", charge=0, name="", elements=[], xyz=[]):
        """Create a new Monomer object from either a filename (.xyz) or a list of
        elements and numpy array containing the .xyz coordinates"""
        self.natoms = 0
        self.nconformers = 1
        self.elements = []
        self.atomtypes = []
        self.xyz = np.array([])
        self.charge = charge
        self.name = name

        if xyzfile != "":
            self.read_xyz(xyzfile)
        elif elements and len(xyz) != 0:
            self.elements = elements
            self.xyz = xyz
            assert len(elements) == len(xyz)
            self.natoms = len(elements)
        else:
            raise ValueError('Monomer elemental and/or xyz data not defined')


        # Default monomer name to match the xyz file
        if name == '':
            xyzname = Path(xyzfile).name.replace('.xyz','')
            self.name = xyzname

    ############################################################################

    ############################################################################
    def __repr__(self):
        return f"{self.__class__.__name__} {self.name} ({self.natoms} atoms, {self.nconformers} conformers)"

    ############################################################################


    ############################################################################
    def __getitem__(self,index):
        conformer = self.xyz[index]
        return Monomer(charge=self.charge, name=f'{self.name}[{index}]', elements=self.elements, xyz=conformer)

    ############################################################################

    ############################################################################
    def read_xyz(self, xyzfile: str):
        """
        Populate Monomer with data from a .xyz file.

        Parameters
        ----------
        xyzfile : str
            Name of .xyz file. Multiple conformers can be passed into the same
            .xyz file so long as the number and ordering of atoms is
            preserved.

        """
        with open(xyzfile, "r") as f:
            lines = f.readlines()

        first = True
        iconformer = 0
        coordinates = []
        try:
            while len(lines) > 0:
                natoms = int(lines.pop(0))
                coordinates.append([])
                if first:
                    self.natoms = natoms
                else:
                    assert (
                        natoms == self.natoms
                    ), "The number of atoms must be constant for each conformer within a .xyz file"
                lines.pop(0)  # Comment line ignored
                for i in range(self.natoms):
                    axyz = lines.pop(0).split()
                    a = axyz[0]
                    if first:
                        self.elements.append(a)
                    else:
                        assert (
                            a == self.elements[i]
                        ), "The ordering of atoms must be constant for each conformer within a .xyz file"

                    xyz = axyz[1:]
                    coordinates[iconformer].append(xyz)

                    assert (
                        len(xyz) == 3
                    ), f"""Each atom must have exactly three coordinates, but in
                    your file {xyzfile} atom {a} in conformer index {iconformer} has
                    {len(xyz)} coordinates. Fix your .xyz file and try again."""
                first = False
                iconformer += 1
        except (AssertionError, TypeError, ValueError) as e:
            print(e)
            raise ValueError(
                f"Improperly formated .xyz file {xyzfile}. See Traceback for additional information"
            )

        self.nconformers = iconformer
        self.xyz = np.array(coordinates,dtype=float)

        if not self.atomtypes:
            self.atomtypes = self.elements  # set as a default for now

        return

    ############################################################################


################################################################################

if __name__ == "__main__":
    import sys

    molecule = Monomer(sys.argv[1])

    print(molecule)
