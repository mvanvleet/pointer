"""Define objects related to the packages and schedulers used to carry out QM tasks."""

import numpy as np
from pint import UnitRegistry
from pint.errors import UndefinedUnitError
from pathlib import Path
from abc import ABC, abstractmethod
import subprocess


from ..config import settings

################################################################################
class QMEngine(ABC):
    """Abstract class for how information about the software package, scheduler, and resource
    requirements for QM jobs should be represented.
    """

    @property
    @abstractmethod
    def input_suffix(self):
        pass

    @property
    @abstractmethod
    def output_suffix(self):
        pass

    @abstractmethod
    def job_status(self, filename):
        pass

    @abstractmethod
    def parse_output(self, filename, calctype):
        pass

    ############################################################################
    def __init__(self,config=settings):
        """Create a new Engine object, by default getting settings from the config file."""
        ureg = UnitRegistry()
        ureg.define('word = 8 * byte')
        self.Quantity = ureg.Quantity
        try:
            self.package = config["qm-engine"]["package"]
            self.memory = self.Quantity( config["qm-engine"]["max_memory"] )
            self.nprocs = config["qm-engine"]["max_nprocs"]
            self.schedulername = config["scheduler"]["scheduler"]
            if self.schedulername != 'bg' or config["qm-engine"].has_key("submitcommand"):
                # submit command required for schedulers, optional for local systems to
                # override default
                self.submitcommand = config["qm-engine"]["submitcommand"]
                self.scheduler = Scheduler(self.schedulername)
            else:
                self.submitcommand = None
                ## self.statuscommand = None
                ## self.delcommand = None

        except KeyError:
            raise KeyError('Missing required input for Engine object')
        except UndefinedUnitError:
            print(
                    '''Units given for memory not understood. 
                    
                    See pint documentation for a full list of accepted units.
                    ''')
            raise

        if not ureg.is_compatible_with(self.memory,'bytes'):
            raise SyntaxError( 'Units given for memory must have a base unit of bytes.')

    ############################################################################

    ############################################################################
    def __repr__(self):
        return f"""{self.__class__.__name__} running package {self.package}. 
        Scheduler: {self.scheduler}
        Job resources: {self.memory} memory, {self.nprocs} CPUs requested per job."""

    ############################################################################

    ################################################################################
    def submit_job(self, filename: str, nprocs:int=None) -> str:
        """
        Submit job for execution.

        Parameters
        ----------
        filename : str
            Name of input file (.com suffix optional)

        Returns
        -------
        jobid : str
            Job Tracking ID (for batch schedulers)
        """

        if not nprocs:
            nprocs = self.nprocs

        # Identify and change to the correct directory (important for PBS since qsub
        # commands must be executed from the workdir
        filepath = Path(filename)
        workdir = filepath.parent
        ifile = filepath.name

        p = subprocess.run([self.submitcommand,'-n',str(nprocs),str(ifile)], check=True,
                    capture_output=True, text=True, cwd=workdir)

        if self.scheduler == 'pbs':
            jobid = p.stdout.split()[-1]
        else:
            jobid = None

        return jobid
        

    ################################################################################

################################################################################


################################################################################
class Scheduler():
    def __init__(self,scheduler='pbs'):
        """Create a new scheduler object"""

        if scheduler.lower() == 'pbs':
            self.statuscommand='qstat'
            self.verboseoption='-f'
            self.delcommand='qdel'
            self.jobname_flag = 'Job_Name'
            self.jobstatus_flag = 'job_state'

            self.running_flag = 'R'
            self.queued_flag = 'Q'

            self.jobstatus = { 'R' : 'running',
                               'Q' : 'queued',
                               'H' : 'failed',
                              }
        else:
            raise NotImplementedError

    def job_status(self,jobid=None,jobname=None):
        if jobid:
            #TODO: Add jobid check here to see if job is queued
            print(jobid)
            info = subprocess.run([self.statuscommand,jobid],capture_output=True)
            print(info)
            print('Need to finish this function')
            sys.exit()
        elif jobname: # Try to locate jobs in queue based on job name
            ret = subprocess.run([self.statuscommand,self.verboseoption], 
                    capture_output=True, encoding='utf-8')
            statusoutput = [line.split() for line in ret.stdout.split('\n')]
            found = False
            for line in statusoutput:
                if line and line[0] == self.jobname_flag:
                    if line[-1] == jobname:
                        found = True
                elif found and line[0] == self.jobstatus_flag:
                    status = self.jobstatus[ line[-1] ]
                    return status
            else: # jobname not located, can assume job not in queue
                return 'none'
        else: 
            raise ValueError('Function must be called with either jobid or jobname variables given')

################################################################################
