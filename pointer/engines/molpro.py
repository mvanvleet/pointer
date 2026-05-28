"""Submit and analyze data from Molpro calculations."""

import xml.etree.ElementTree as ET
import pathlib
import subprocess

from .engine import QMEngine
from .inputfiles.molpro_sapt import sapt_pbe0_ct_template, avtz_ip_template
from ..molecules import Monomer
# from pymolpro import Project

################################################################################
class Molpro(QMEngine):

    input_suffix = ".com"
    output_suffix = ".out"

    default_executable = 'molpro'

    sapt_template = sapt_pbe0_ct_template
    ip_template = avtz_ip_template

    xyz_format = '{:2} {:>16.8f} {:16.8f} {:>16.8f}\n'

    ################################################################################
    def __init__(self):
        QMEngine.__init__(self)
    ################################################################################

    ################################################################################
    def create_ip_job(self, inputfile: str, monomer : Monomer, iconformer=0):
        """
        Create Ionization Potential Calculation job for later execution.

        Parameters
        ----------
        inputfile : str
            Name of Molpro input file (.com suffix optional)
        monomer : Monomer
            Molecule to include in the calculation

        Returns
        -------
        None
        """

        memory = int(self.memory.to('megawords')._magnitude)
        charge = monomer.charge
        ion_charge = charge + 1
        xyz = monomer.xyz[iconformer]
        atoms = monomer.elements
        jobtemplate = self.ip_template

        geometry = ''
        for atom,coord in zip(atoms, xyz):
            geometry += self.xyz_format.format(atom,*coord)

        job = jobtemplate.format(**locals())
        inputfile = pathlib.Path(inputfile).with_suffix(self.input_suffix)
        with open(inputfile,'w') as f:
            f.write(job)

        return 
    ################################################################################

    ################################################################################
    def create_sapt_job(self, inputfile: str, 
                            monomerA : Monomer, monomerB : Monomer,
                            acshift_mona, acshift_monb, 
                            midbonds=True, basis='avtz'):
        """
        Create SAPT-DFT job for later execution.

        Parameters
        ----------
        inputfile : str
            Name of Molpro input file (.com suffix optional)
        monomerA : Monomer
            First monomer in the dimer 
        monomerB : Monomer
            Second monomer in the dimer 
        acshift_mona : float
            GRAC asymptotic correction parameter for Monomer A
        acshift_monb : float
            GRAC asymptotic correction parameter for Monomer B
        midbonds : bool, optional, default: True
            Whether to include an even-tempered basis function in between the centers of
            mass of the two monomers

        Returns
        -------
        None
        """

        memory = int(self.memory.to('megawords')._magnitude)
        mona, monb = monomerA, monomerB
        qmona = mona.charge
        qmonb = monb.charge
        qdimer = qmona + qmonb
        mona_xyz = mona.xyz
        monb_xyz = monb.xyz
        mona_atoms = mona.elements
        monb_atoms = mona.elements
        jobtemplate = self.sapt_template
        imona = ', '.join([str(i) for i in range(mona.natoms)])
        imonb = ', '.join([str(i) for i in range(mona.natoms,mona.natoms+monb.natoms)])

        geometry = ''
        for atom,coord in zip(mona_atoms, mona_xyz):
            geometry += self.xyz_format.format(atom,*coord)
        for atom,coord in zip(monb_atoms, monb_xyz):
            geometry += self.xyz_format.format(atom,*coord)
        
        job = jobtemplate.format(**locals())
        inputfile = pathlib.Path(inputfile).with_suffix(self.input_suffix)
        with open(inputfile,'w') as f:
            f.write(job)

        exit()

        return 

    ################################################################################

    ## ################################################################################
    ## def submit_job(self, filename: str, nprocs:int=None) -> str:
    ##     """
    ##     Submit job for execution.

    ##     Parameters
    ##     ----------
    ##     filename : str
    ##         Name of Molpro input file (.com suffix optional)

    ##     Returns
    ##     -------
    ##     jobid : str
    ##         Job Tracking ID (for batch schedulers)
    ##     """

    ##     if not nprocs:
    ##         nprocs = self.nprocs

    ##     # Identify and change to the correct directory (important for PBS since qsub
    ##     # commands must be executed from the workdir
    ##     filepath = pathlib.Path(filename)
    ##     workdir = filepath.parent
    ##     ifile = filepath.name

    ##     p = subprocess.run([self.submitcommand,'-n',str(nprocs),str(ifile)], check=True,
    ##                 capture_output=True, text=True, cwd=workdir)

    ##     if self.scheduler == 'pbs':
    ##         jobid = p.stdout.split()[-1]
    ##     else:
    ##         jobid = None

    ##     return jobid
    ##     

    ## ################################################################################

    ################################################################################
    def job_status(self, filename: str, verbose=False, jobid=None) -> str:
        """
        Determine if Molpro job has successfully finished, failed with errors, or is still
        running.

        Parameters
        ----------
        filename : str
            Path to Molpro output file (.out suffix optional)
        jobid : int, optional
            jobid from scheduler to check job status

        Returns
        -------
        status : {'completed', 'failed', 'running', 'queued','none'}
            Job status ('none' indicates job status appears unstarted)
        """

        #TODO: Make status also representable by one letter codes: C, F, R, Q, N

        basepath = pathlib.Path(filename).with_suffix('')
        basename = basepath.name
        outfile = basepath.with_suffix(self.output_suffix)

        # First check if job is queued but not yet running
        if not outfile.exists():
            status_in_queue = self.scheduler.job_status(jobid,basename)
            if status_in_queue:
                return status_in_queue
            else:
                return 'none'

        # Next sort through jobs with an output file 
        finished = False
        errors = False

        with open(outfile, "r") as f:
            lastline = f.readlines()[-1]
        if "Molpro calculation terminated" in lastline:
            finished = True

        if finished:
            xmlfile = basepath.with_suffix(".xml")
            tree = ET.parse(xmlfile)
            xmlns = "http://www.molpro.net/schema/molpro-output"
            err = tree.findall(
                "xmlns:job/xmlns:jobstep/xmlns:error", namespaces={"xmlns": xmlns}
            )

            if err:
                if verbose:
                    for e in err:
                        print("Error Found:", e.attrib)
                errors = True

        if errors:
            return "failed" 
        elif finished:
            return "completed"
        else:
            status_in_queue = self.scheduler.job_status(jobid,basename)
            if not status_in_queue:
                # Looks like job crashed mysteriously without a Molpro error
                return 'failed'
            return status_in_queue

    ################################################################################


    ################################################################################
    def parse_output(self, filename: str,calctype: str ):
        """
        Parse a Molpro output file. 

        Parameters
        ----------
        filename : str
            Name of Molpro output file 
        calctype : {'acshift','sapt'}
            Calculation type

        Returns
        -------
        output
            Tuple containing data specific to calculation type
        """

        if calctype.lower() == 'acshift':
            return self.parse_ionization(filename)
        else:
            raise NotImplementedError
    ################################################################################

    ################################################################################
    def parse_ionization(self, filename: str) -> (float, float):
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
                ip_magnitude = float(line.split()[-2])
                got_ip = True
            elif HOMO_FLAG in line and got_homo == False:
                homo_magnitude = float(line.split()[2])
                got_homo = True
            else:
                continue
        else:
            raise ValueError(
                f"""Could not find HOMO and IP data. Check the Molpro output file
                {filename} for errors."""
            )

        ip = self.Quantity(ip_magnitude,'hartree')
        homo = self.Quantity(homo_magnitude,'hartree')

        return ip, homo


    ################################################################################

if __name__ == "__main__":
    import sys

    Molpro.parse_ionization(sys.argv[1])
