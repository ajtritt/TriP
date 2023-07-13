import abc
import json

class CromwellJob(abc.ABCMeta):

    cw_jar = "/global/common/software/m3408/cromwell-54.jar"

    def __init__(self, inputs_dict, config, **xx_args):
        self.inputs = inputs_dict
        self.wdl = config['wdl']
        self.shifter_conf = config['shifter_conf']
        self.xx_args = xx_args
        self.outdir = None
        self.jobid = None

    @classmethod
    def write_sbatch(cls, f, outbase, wdl, shifter_conf, time=720, dep=None, **xx):
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
        kwargs['qos'] = 'regular'
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
        kwargs['job-name'] = job_name
        if dep is not None:
            kwargs['dependency'] = dep
        for k, v in kwargs.items():
            write(f"#SBATCH --{k}={v}")
        write()
        write(f"cd {outbase}.$SLURM_JOB_ID")
        write()
        xx_args = " ".join([f"-XX:{k}={v}" for k, v in xx.items()])

        write(f"java {xx_args} -Dconfig.file={shifter_conf} -jar {cls.cw_jar} run -m metadata.json -i inputs.json {wdl}")

        return tmp_sh

    def submit_workflow(self, outbase, submit=True, dep=None):
        inputs_f, inputs_path = tempfile.mkstemp(suffix='.json')
        json.dump(self.inputs, inputs_f, indent=2)

        sh_f, sh_path = tempfile.mkstemp(suffix='.sh')
        self.write_sbatch(sh, outbase, self.wdl, self.shifter_conf, dep=dep, **self.xx_args)

        jobid = None
        if submit:
            jobid = self._submit_job(sh_path)
            if jobid == -1:
                exit()
            outdir = f"{outbase}.{jobid}"

            os.mkdirs(outdir)
            shutil.copyfile(sh_path, f"{outdir}.sh")
            shutil.copyfile(inputs_path, f"{outdir}/inputs.json")

        self.outdir = outdir
        self.jobid = jobid
        return outdir, jobid

    def _submit_job(self, path, conda_env=None):
        cmd = f'sbatch {path}'
        if conda_env is not None:
            cmd = f'conda run -n {conda_env} {cmd}'
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

    def get_final_output(self, filename)
        if self.outdir is not None:
            return os.path.join(self.outdir, filename)
        return None


class QCJob(CromwellJob):

    def __init__(self, fastq, config):
        inputs = {
            "jgi_rqcfilter.database": config['database'],
            "jgi_rqcfilter.input_files": [fastq],
            "jgi_rqcfilter.input_interleaved": True,
            "jgi_rqcfilter.input_fq1": [],
            "jgi_rqcfilter.input_fq2": [],
            "jgi_rqcfilter.outdir": "./",
            "jgi_rqcfilter.memory": "35G",
            "jgi_rqcfilter.threads": "16"
        }
        super().__init__(inputs, config)
        self._output_fq = os.path.basename(fastq).replace('.fastq', '.anqdpht.fastq')

    @property
    def cleaned_fastq(self):
        return self.get_final_output(self._output_fq)


class AssemblyJob(CromwellJob):

    def __init__(self, fastq, config):
        inputs = {
            "jgi_metaASM.input_file":[fastq],
            "jgi_metaASM.rename_contig_prefix": config['rename_contig_prefix'],
            "jgi_metaASM.outdir": ".",
            "jgi_metaASM.input_interleaved": True,
            "jgi_metaASM.input_fq1":[],
            "jgi_metaASM.input_fq2":[],
            "jgi_metaASM.memory": "105G",
            "jgi_metaASM.threads": "16"
        }
        super().__init__(inputs, config)
        self._output_fna = "assembly_scaffolds.fna"
        self._output_bam = "pairedMapped_sorted.bam"

    @property
    def assembly_fasta(self):
        return self.get_final_output(self._output_fna)

    @property
    def mapped_reads(self):
        return self.get_final_output(self._output_bam)


class RBAJob(CromwellJob):

    def __init__(self, fastq, config):
        inputs = {
              "ReadbasedAnalysis.input_file": fastq,
              "ReadbasedAnalysis.paired": True,
              "ReadbasedAnalysis.prefix": "TEST",
              "ReadbasedAnalysis.cpu": 8,
              "ReadbasedAnalysis.proj": "TEST",
              "ReadbasedAnalysis.resource": "NERSC - PERLMUTTER",
              "ReadbasedAnalysis.informed_by": "None"
            }

class AnnotationJob(CromwellJob):

    def __init__(self, fasta, config):
        inputs = {
              "annotation.input_file": fasta,
              "annotation.imgap_project_id": prefix,
              "annotation.proj": prefix,
              "annotation.resource": "NERSC - PERLMUTTER",
              "annotation.informed_by": "None"
            }



if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('fastq', help='The interleaved Fastq to run workflow with')


    # CromwellJob(inputs_dict, wdl, shifter_conf, **xx_args):

    raw_fastq = args.fastq
    with open(args.config, 'rb') as f:
        config = tomllib.load(f)

    qc_wdl = config['qc']['wdl']
    rqc_db = config['qc']['database']
    qc_

    qc_inputs = get_qc_io(rqc_db, raw_fastq)
    qc_job = CromwellJob(qc_inputs, qc_wdl, )
    qc_outdir, qc_jobid = qc_job.submit_workflow(...)


    asm_job = CromwellJob(...)

    outdir, asm_jobid = asm_job.submit_workflow(...)



    _job = CromwellJob(...)

    _job.submit_workflow(..., dep=asm_jobid)





