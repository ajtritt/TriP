if [ which parallel > /dev/null 2>&1 ]; then
    echo "parallel command not found. Please load parallel module"
    exit 1
fi


echo "Downloading BBTools package"
curl -J -O -L https://sourceforge.net/projects/bbmap/files/latest/download
tar -xzf BBMap_*.tar.gz

func=`mktemp --suffix=.sh`
echo "Saving temporary function for running parallel in $func"

echo \
"R1=\$1
R2=\`echo \$R1 | sed -e 's/_R1_/_R2_/g'\`
ROUT=\`echo \$R1 | sed -e 's/_R1_/_/g'\`
bbmap/reformat.sh in1=\$R1 in2=\$R2 out=interleaved/\$ROUT overwrite=true" > $func

echo "Reformatting `ls *_R1_*.fastq.gz | wc -l` paired fastqs"
ls *_R1_*.fastq.gz | parallel -j 10 bash $func
