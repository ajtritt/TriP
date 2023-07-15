import abc
import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib

class CromwellJob(metaclass=abc.ABCMeta):

    job_type = None

    def __init__(self, inputs_dict, config, sample, **xx_args):
        assert self.job_type is not None
        self.inputs = inputs_dict
        self.wdl = config['wdl']
        self.cw_jar = config['cw_jar']
        self.shifter_conf = config['shifter_conf']
        self.xx_args = xx_args
        self.outdir = None
        self.jobid = None
        self.sample = sample

    @staticmethod
    def load_config(config_file):
        with open(config_file, 'rb') as f:
            config = tomllib.load(f)

        global_conf = config.pop('global', dict())
        for conf in config.values():
            conf.update(global_conf)

        return config

    @classmethod
    def write_sbatch(cls, f, outbase, wdl, shifter_conf, cw_jar, time=720, dep=None, qos='regular', env=None, **xx):
        """
        The inputs JSON is expected to be in the directory that the job will change into

        Args:
            f               : the stream to write the script to
            outbase         : the basename for the output directory and log file
            wdl             : the WDL file to run with Cromwell
            shifter_conf    : the Shifter config file to use when running Cromwell
        """

        write = lambda s="": print(s, file=f)

        write("#!/bin/bash")
        kwargs = dict()
        kwargs['qos'] = qos
        kwargs['time'] = time
        kwargs['output'] = f"{outbase}.%j.log"
        kwargs['error'] = kwargs['output']
        kwargs['nodes'] = 1
        kwargs['ntasks'] = 1
        kwargs['cpus-per-task'] = 32
        kwargs['mail-type'] = 'END,FAIL'
        kwargs['mail-user'] = 'ajtritt@lbl.gov'
        kwargs['constraint'] = 'cpu'
        kwargs['account'] = 'm3408'
        kwargs['job-name'] = cls.job_type + "." + os.path.basename(outbase)
        if dep is not None:
            kwargs['dependency'] = dep
        for k, v in kwargs.items():
            write(f"#SBATCH --{k}={v}")
        write()
        if isinstance(env, dict):
            for k, v in env.items():
                write(f"export {k}={v}")
            write()
        write(f"cd {outbase}.$SLURM_JOB_ID")
        write()
        xx_args = " ".join([f"-XX:{k}={v}" for k, v in xx.items()])

        write(f"java {xx_args} -Dconfig.file={shifter_conf} -jar {cw_jar} run -m metadata.json -i inputs.json {wdl}")

    def submit_workflow(self, outbase, submit=True, dep=None, debug=False, **extra_kwargs):
        inputs_f, inputs_path = tempfile.mkstemp(suffix='.json')
        inputs_f = tempfile.NamedTemporaryFile('w', suffix='.json')
        inputs_path = inputs_f.name
        json.dump(self.inputs, inputs_f, indent=2)
        inputs_f.flush()

        sh_f = tempfile.NamedTemporaryFile('w', suffix='.sh')
        sh_path = sh_f.name
        kwargs = {'dep': dep}
        kwargs.update(self.xx_args)
        if debug:
            kwargs['time'] = 20
            kwargs['qos'] = 'debug'
        # kwargs['env'] = {'STEP': self.job_type, 'SAMPLE': self.sample}
        self.write_sbatch(sh_f, outbase, self.wdl, self.shifter_conf, self.cw_jar, **kwargs)
        sh_f.flush()

        outdir = sh_path

        jobid = None
        if submit:
            jobid = self._submit_job(sh_path)
            if jobid == -1:
                exit()
            outdir = f"{outbase}.{jobid}"

            os.makedirs(outdir)
            shutil.copyfile(sh_path, f"{outdir}.sh")
            shutil.copyfile(inputs_path, f"{outdir}/inputs.json")
        else:
            with open(inputs_path, 'r') as f:
                print(f.read())
            print()
            with open(sh_path, 'r') as f:
                print(f.read())

        self.outdir = outdir
        self.jobid = jobid
        return outdir, jobid

    def _submit_job(self, path):
        cmd = f'sbatch {path}'
        print(cmd)
        output = subprocess.check_output(
                    cmd,
                    stderr=subprocess.STDOUT,
                    shell=True).decode('utf-8')

        result = re.search('Submitted batch job (\d+)', output)
        if result is not None:
            ret = int(result.groups(0)[0])
        else:
            print(f'Job submission failed: {output}')
            ret = -1
        return ret

    def get_final_output(self, filename):
        if self.outdir is not None:
            return os.path.join(self.outdir, filename)
        return None

    @abc.abstractmethod
    def get_outputs(self):
        pass

    @classmethod
    def add_bp_args(cls, parser):
        parser.add_argument('-o', '--outdir', type=str, help='the output directory for the job', default='.')
        parser.add_argument('-s', '--submit', action='store_true', help='submit job', default=False)
        parser.add_argument('-d', '--debug', action='store_true', help='submit to debug queue', default=False)

    @classmethod
    @abc.abstractmethod
    def add_args(self, parser):
        pass

    @classmethod
    @abc.abstractmethod
    def run(cls, **config):
        pass

# class AssemblyJob(CromwellJob):
#
#     def __init__(self, config, *inputs):
#         fastq = inputs[0]
#         inputs = {
#             "jgi_metaASM.input_file":[fastq],
#             "jgi_metaASM.rename_contig_prefix": config['rename_contig_prefix'],
#             "jgi_metaASM.outdir": ".",
#             "jgi_metaASM.input_interleaved": True,
#             "jgi_metaASM.input_fq1":[],
#             "jgi_metaASM.input_fq2":[],
#             "jgi_metaASM.memory": "105G",
#             "jgi_metaASM.threads": "16"
#         }
#         super().__init__(inputs, config)
#         self._output_fna = "assembly_scaffolds.fna"
#         self._output_bam = "pairedMapped_sorted.bam"
#
#     @property
#     def assembly_fasta(self):
#         return self.get_final_output(self._output_fna)
#
#     @property
#     def mapped_reads(self):
#         return self.get_final_output(self._output_bam)
#
#
# class RBAJob(CromwellJob):
#
#     def __init__(self, config, *inputs):
#         fastq = inputs[0]
#         inputs = {
#               "ReadbasedAnalysis.input_file": fastq,
#               "ReadbasedAnalysis.paired": True,
#               "ReadbasedAnalysis.prefix": "TEST",
#               "ReadbasedAnalysis.cpu": 8,
#               "ReadbasedAnalysis.proj": "TEST",
#               "ReadbasedAnalysis.resource": "NERSC - PERLMUTTER",
#               "ReadbasedAnalysis.informed_by": "None"
#             }
#
# class AnnotationJob(CromwellJob):
#
#     def __init__(self, config, *inputs):
#         fasta = inputs[0]
#         prefix = inputs[1]
#         inputs = {
#               "annotation.input_file": fasta,
#               "annotation.imgap_project_id": prefix,
#               "annotation.proj": prefix,
#               "annotation.resource": "NERSC - PERLMUTTER",
#               "annotation.informed_by": "None"
#             }
#
#
