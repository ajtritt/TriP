from .workflow import Workflow

# {
#   "jgi_metaASM.input_file":["/global/cfs/projectdirs/m3408/ficus/11809.7.220839.TCCTGAG-ACTGCAT.fastq.gz"],
#   "jgi_metaASM.rename_contig_prefix":"503125_160870",
#   "jgi_metaASM.input_interleaved":true,
#   "jgi_metaASM.input_fq1":[],
#   "jgi_metaASM.input_fq2":[],
#   "jgi_metaASM.outdir":"/global/cfs/projectdirs/m3408/aim2/metagenome/assembly/ficus/503125_160870"
# }


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

class AssemblyWorkflow(Workflow):

    def __init__(self, input_fastq, output_directory):
        self.data = dict()
        self.data["jgi_metaASM.input_interleaved"] = true
        self.data["jgi_metaASM.input_file"] = input_fastq
        self.data["jgi_metaASM.outdir"] = output_directory

    def get_inputs_dict(self):
        return self.data
