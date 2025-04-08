import time
import argparse
import os

def main(target_tf,blastfile,outfile ):
    with open(target_tf,'r') as targetfile_handle:
        target_tf_set = set()
        for line in targetfile_handle:
            line = line.strip()
            id = line.split('\t')[1] + '@@@' + line.split('\t')[0]
            target_tf_set.add(id)
    print(f'target_tf种类的数量是{len(target_tf_set)}')
    with open(blastfile ,'r') as blastfile_handle, open(outfile,'w') as outfile_handle:
        blast_id_set = set()
        for line_blast in blastfile_handle:
            line_blast = line_blast.strip()
            blast_id = line_blast.split('\t')[1].split('@@@')[0] + '@@@' + line_blast.split('\t')[1].split('@@@')[1]
            
            if blast_id in target_tf_set:
                blast_id_set.add(blast_id)
                outfile_handle.write(line_blast+'\n')
    print(f'blast中找打的符合要求的转录因子种类数量是{len(blast_id_set)}')

if __name__ == '__main__':
    # parameter parse
    my_parser = argparse.ArgumentParser(allow_abbrev=False, add_help=True, prefix_chars='-',description='Help information')  #allow_abbrev: allow to abbreviate argv or not
    my_parser.add_argument('--blast', type=str,required=False, help='the sort blast file')
    my_parser.add_argument('--outfile', '-o', type=str,required=False, help='outputfile')
    my_parser.add_argument('--target_tf',  type=str, required=False,help='the target tf information generateed by using fimo in sequence provided')
 
    args = my_parser.parse_args()  # class argsparse namespace

    blastfile = os.path.abspath(args.blast)
    outfile = os.path.abspath(args.outfile)
    target_tf = os.path.abspath(args.target_tf)

    main(target_tf,blastfile,outfile)

