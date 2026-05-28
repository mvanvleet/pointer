"""Perform SAPT calculations on molecular dimers.
parameters needed for SAPT calculations."""

#from . import molpro
from ..config import settings
from ..molecules import Monomer
import pathlib
import importlib
import numpy as np
from time import sleep

################################################################################
def submit_job(jobname, monomerA: Monomer, monomerB: Monomer, 
        acshift_mona : float, acshift_monb : float,
        midbonds=True, forcesubmit=False, wait=False):
    """
    Submit DFT-SAPT calculation(s) to the QM engine. 

    https://psicode.org/psi4manual/master/sapt.html

    Parameters
    ----------
    jobname : str or Path
        jobname (suffix optional)
    monomerA : Monomer
        First monomer in the dimer (should only have one conformer)
    monomerB : Monomer
        Second monomer in the dimer (should only have one conformer)
    acshift_mona : float
        GRAC asymptotic correction parameter for Monomer A
    acshift_monb : float
        GRAC asymptotic correction parameter for Monomer B
    midbonds : bool, default: True
        Whether to include an even-tempered midbond function between the centers of mass of the two
        monomers. Generally recommended.
    forcesubmit : bool, optional, default: False
        Force submission of the SAPT calculation, even if already run successfully
    """

    engine_name = settings["qm-engine"]["package"]
    if engine_name.lower() != "molpro":
        raise NotImplementedError(
            f"SAPT calculations using package '{engine}' are not supported at this time"
        )
    else:
        try: 
            # invoke an engine instance from the user-specified library
            engine = getattr(importlib.import_module(f".{engine_name}",
                package='pointer.engines'), f"{engine_name.capitalize()}")()
        except ImportError: 
            print(f"Engine {engine_name} not supported")
            raise


    # Submit SAPT calculation (if needed)
    parentdir = pathlib.Path(settings["paths"]["saptdir"])
    parentdir.mkdir(parents=True, exist_ok=True)
    jobids = []
    outfiles = []
    ifiles = [pathlib.Path(jobname)]
    for i,filename in enumerate(ifiles):
        inputfile = parentdir / filename.with_suffix(engine.input_suffix)
        outfile = inputfile.with_suffix(engine.output_suffix)

        if engine.job_status(outfile) in ['completed','running','queued'] and not forcesubmit:
            jobids.append(None)
            outfiles.append(outfile)
            continue # don't modify or submit this job
        else:
            engine.create_sapt_job(inputfile,monomerA, monomerB, acshift_mona, acshift_monb, midbonds)
            jobid = engine.submit_job(inputfile)
            jobids.append(jobid)
            outfiles.append(outfile)

    # Check through job queue (once if wait==False, until completion if wait==True) to
    # see if jobs have finished running
    finished = False
    if wait:
        print('Waiting for SAPT calculation to complete',end='',flush=True)
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
        print('.',flush=True)
        print('SAPT job completed')
        return 

    return
################################################################################




if __name__ == "__main__":
    import sys

