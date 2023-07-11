DIR="pmkczfzhx/Un_DTSA760/Project_ABHS_Nova835P_Savage"
module load parallel
rsync -LrRtv slimsdata.genomecenter.ucdavis.edu::slims/$DIR/@md5Sum.md5 .
awk -F '  ' '{print $2}' $DIR/@md5Sum.md5 | parallel -j 6 rsync -LrRtv slimsdata.genomecenter.ucdavis.edu::slims/$DIR/{} .
