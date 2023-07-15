import os

from .workflow import CromwellJob

class QCJob(CromwellJob):
    """Run QC pipeline on a Fastq"""

    job_type = 'qc'

    def __init__(self, config, fastq, sample):
        inputs = {
            "nmdc_rqcfilter.database": os.path.expandvars(config['database']),
            "nmdc_rqcfilter.input_files": fastq,
            "nmdc_rqcfilter.proj": f"trip_bnt-{sample}-qc",
            "nmdc_rqcfilter.resource": f"NERSC -- perlmutter",
            "nmdc_rqcfilter.informed_by": "None"
        }
        super().__init__(inputs, config, sample)
        self._output_fq = os.path.basename(fastq).replace('.fastq', '.anqdpht.fastq')

    def get_outputs(self):
        return [self.cleaned_fastq]

    @property
    def cleaned_fastq(self):
        return self.get_final_output(self._output_fq)

    @classmethod
    def add_args(self, parser):
        parser.add_argument('fastq', help='the raw Fastq to run QC on')

    @classmethod
    def run(cls, **config):
        fastq = os.path.abspath(config['fastq'])
        outbase = '_'.join(os.path.basename(fastq.strip('.gz').strip('.fastq')).split('_')[:2])

        job = cls(config['qc'], fastq, outbase)
        return job.submit_workflow(os.path.join(config['outdir'], outbase), **config)#submit=config['submit'])
