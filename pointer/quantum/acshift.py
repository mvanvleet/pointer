"""Calculate and analyze ionization potentials (IP) to compute the GRAC shift
parameters needed for SAPT calculations."""

from ..config import settings
from ..molecules import Monomer
import pathlib
import importlib
import numpy as np
from time import sleep

################################################################################
def get_acshift(monomer: Monomer, conformers="ignore", forcesubmit=False, wait=False) -> float:
    """
    Submit IP calculation(s) to the QM engine. 
    and process the results to obtain the GRAC asymptotic shift correction.

    https://psicode.org/psi4manual/master/sapt.html

    Parameters
    ----------
    monomer : Monomer
        Monomer on which to perform the calculations
    conformers : {'ignore','all','average'}
        Whether only the first conformer should be used to calculate the AC shift, if
        separate calculations should be run for each conformer, or if conformers should
        be averaged to get the AC shift
    forcesubmit : bool, optional, default: False
        Force submission of all IP calculations, even those that have already run
        successfully
    wait: bool, optional, default: False
        Wait to return until job(s) have completed successfully.

    Returns
    -------
    acshift : float
        The GRAC asymptotic correction parameter. Only returned if all calculations have
        finished, otherwise function returns None.


    """

    conformers = conformers.lower()

    engine_name = settings["qm-engine"]["package"]
    if engine_name.lower() != "molpro":
        raise NotImplementedError(
            f"Calculations using package '{engine}' are not supported at this time"
        )
    else:
        try: 
            # invoke an engine instance from the user-specified library
            engine = getattr(importlib.import_module(f".{engine_name}",
                package='pointer.engines'), f"{engine_name.capitalize()}")()
        except ImportError: 
            print(f"Engine {engine_name} not supported")
            raise

    # Name the IP calculation(s)
    suffix = engine.input_suffix
    if conformers == "ignore":
        ifiles = [f"{monomer.name}_ip{suffix}"]
    elif conformers in ["average","all"]:
        ifiles = [
            f"{monomer.name}_ip_conf{i}{suffix}" for i in range(monomer.nconformers)
        ]
    else:
        raise ValueError("Conformers argument must be either 'all','ignore','average'")

    # Submit IP calculations (as needed)
    parentdir = pathlib.Path(settings["paths"]["acshiftdir"])
    parentdir.mkdir(parents=True, exist_ok=True)
    jobids = []
    outfiles = []
    for i,filename in enumerate(ifiles):
        inputfile = parentdir / filename
        outfile = inputfile.with_suffix(engine.output_suffix)

        if engine.job_status(outfile) in ['completed','running','queued'] and not forcesubmit:
            jobids.append(None)
            outfiles.append(outfile)
            continue # don't modify or submit this job
        else:
            engine.create_ip_job(inputfile,monomer,iconformer=i)
            jobid = engine.submit_job(inputfile)
            jobids.append(jobid)
            outfiles.append(outfile)

    # Check through job queue (once if wait==False, until completion if wait==True) to
    # see if jobs have finished running
    finished = False
    if wait:
        print('Waiting for IP calculations to complete (may take awhile)',end='',flush=True)
    while not finished:
        status = [None for job in jobids]
        for i, (filename,job) in enumerate(zip(outfiles,jobids)):
            status[i] = engine.job_status(filename,job)
            if status[i] == 'failed':
                raise RuntimeError(f'Job {filename} failed. Check the output file and re-run.')
        finished = np.all([True if job in ['completed','failed'] else False for job in status ])
        if finished==False and wait==False:
            return 
        elif finished==False and wait:
            print('.',end='',flush=True)
            sleep(10)
    else:
        print('')

    # Process output from completed jobs
    all_ip = np.zeros_like(outfiles)
    all_homo = np.zeros_like(outfiles)
    for i, outfile in enumerate(outfiles):
        #outfile = ifile.replace(suffix,engine.output_suffix)
        ip, homo = engine.parse_output(outfile,calctype='acshift')
        all_ip[i] = ip
        all_homo[i] = homo

    if conformers == 'all':
        acshift = all_ip + all_homo
    else:
        acshift = np.average(all_ip) + np.average(all_homo)

    return acshift

################################################################################


## ################################################################################
## def submit_ip(engine, xyz, qatom):
##     """
##     Submit an ionization potential job to the scheduler.
## 
##     Parameters
##     ----------
##     package : str, optional, default: "molpro"
##         Software package used in the calculation. Currently only Molpro is
##         supported.
##     scheduler : str, optional, default: "pbs"
##         Scheduler used in the calculation. Currently only PBS is
##         supported.
## 
##     Returns
##     -------
##     status : bool
##         True if job submitted without errors
## 
##     """
## 
##     if package != "molpro":
##         return NotImplementedError("Only the Molpro QM package is currently supported.")
## 
##     return NotImplementedError
## 
## 
## ################################################################################


## ################################################################################
## def parse_output(filename: str, package="molpro") -> (float, float):
##     """
##     Parse an output file to extract IP and HOMO data.
## 
##     Parameters
##     ----------
##     filename : str
##         Name of output file containing results of the ionization potential
##         calculation.
##     package : str, Optional, default: "molpro"
##         Software package used in the calculation. Currently only Molpro is
##         supported.
## 
##     Returns
##     -------
##     ip : float
##         Ionization Potential in a.u.
##     homo : float
##         HOMO (highest occupied Molecular Orbital) in a.u.
##     """
## 
##     if package != "molpro":
##         return NotImplementedError
##     else:
##         ip, homo = molpro.process_ionization(filename)
## 
##     return ip, homo
## 
## 
## ################################################################################


if __name__ == "__main__":
    import sys

    # print("IP, HOMO")
    # print(parse_output(sys.argv[1], package="molpro"))
