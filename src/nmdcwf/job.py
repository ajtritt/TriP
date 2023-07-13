

# #!/bin/bash
# #SBATCH --qos=regular
# #SBATCH --time=1800:00
# #SBATCH --output=/global/project/projectdirs/m3408/aim2/metagenome/assembly/503125_160870.log
# #SBATCH --nodes=1
# #SBATCH --ntasks=1
# #SBATCH --cpus-per-task 32
# #SBATCH --mail-type=END,FAIL
# #SBATCH --mail-user=your@email.com
# #SBATCH --constraint=haswell
# #SBATCH --account=m3408
# #SBATCH --job-name=asm_jgi_test
#
# #OpenMP settings:
# #export OMP_NUM_THREADS=8
# #export OMP_PLACES=threads
# #export OMP_PROC_BIND=spread
#
# cd /global/cfs/projectdirs/m3408/aim2/metagenome/assembly
#
# java -XX:ParallelGCThreads=32 -Dconfig.file=shifter.conf -jar /global/common/software/m3408/cromwell-45.jar run -m metadata_out.json -i input.json jgi_assembly.wdl


def write_sbatch(f, outbase, input_json, wdl, shifter_conf, time=720, **xx):
    """
    Args:
        f               : the stream to write the script to
        outbase         : the basename for the output directory and log file
        input_json      : the input JSON file to use
        wdl             : the WDL file to run with Cromwell
        shifter_conf    : the Shifter config file to use when running Cromwell
    """

    cw_jar = "/global/common/software/m3408/cromwell-54.jar"

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
    for k, v in kwargs.items():
        write(f"#SBATCH --{k}={v}")
    write()
    outdir = f"{outbase}.$SLURM_JOB_ID"
    write(f"mkdir {outdir}")
    write(f"cd {outdir}")
    write()
    xx_args = " ".join([f"-XX:{k}={v}" for k, v in xx.items()])

    write(f"java {xx_args} -Dconfig.file={shifter_conf} -jar {cw_jar} run -m metadata.json -i {input_json} {wdl}")

    return tmp_sh
