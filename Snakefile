###########################
# Snakefile for TF finding
# Author: Leiyu Yan
# Date: 2024-04-25
# Version: 1.0
# Description: This Snakefile is used to find TF of jarspar in protein sequences provided by user.
# Usage: snakemake --cores 16
# Output: the jarspar TF in protein sequences information，the jarspar TFs protein sequence that have uniprot id
# Input: protein.fasta,jarspar's meme file,the cared TF list file
###########################
configfile:'./config/config.yaml'
## 软件主目录
SOFTWARE_HOME = config["software_home"] if config["software_home"] else os.getcwd()

rule all:
    input:
        # 配置文件
        f"{config['workdir']}/log/get_jarspar_tf_protein_sequence.log",
        f"{config['workdir']}/log/makeblastdb.log",
        f"{config['workdir']}/log/blastp.log",
        f"{config['workdir']}/log/find_target_tf_in_genome.log",

        # 第一步的结果文件
        TF_protein = f"{config['workdir']}/jarspar/{config['jarspar_type']}/jarspar_tf_protein_sequence.fasta",
        jarspar_mapping_uniprot = f"{config['workdir']}/jarspar/{config['jarspar_type']}/jarspar_mapping_uniprot.xls",
        
        # 第二步建库的结果文件
        protein_db = multiext(f"{config['workdir']}/protein_db/jarspar_tf_protein_db", ".pdb", ".phr", ".pin", ".pjs", ".pot", ".psq", ".ptf", ".pto"),
        
        # 第三步比对的结果文件
        blastp_out = f"{config['workdir']}/blast/pep_blastout.xls",
        blastp_out_sort_gene_in_genome = f"{config['workdir']}/blast/pep_blastout_sort_gene_in_genome.xls",
        blastp_out_sort_jarspar_tf = f"{config['workdir']}/blast/pep_blastout_sort_jarspar_tf.xls",
        
        # 第四步，在基因组蛋白质序列库中寻找指定的TF的同源基因
        target_tf_in_genome = f"{config['workdir']}/target_tf_in_genome/target_tf_in_genome_blastout.xls",


rule get_jarspar_tf_protein_sequence:
    input:
        meme = config['CORE_plants_meme'],
    output:
        TF_protein = f"{config['workdir']}/jarspar/{config['jarspar_type']}/jarspar_tf_protein_sequence.fasta",
        jarspar_mapping_uniprot = f"{config['workdir']}/jarspar/{config['jarspar_type']}/jarspar_mapping_uniprot.xls",
    params:
        workdir = f"{config['workdir']}/jarspar/{config['jarspar_type']}/",
        threads = config['pool_threads'],# the number of threads to use in parse URL
        python = config['python']
    log:
        f"{config['workdir']}/log/get_jarspar_tf_protein_sequence.log"
    shell:
       # "python ./script/get_jarspar_tf_protein_sequence.py -i {input.meme} -o {params.workdir} -t {params.threads}"
       """
       {params.python} {SOFTWARE_HOME}/script/get_jarspar_tf_protein_sequence_ProcessPool.py -i {input.meme} -o {params.workdir} -t {params.threads} 1> {log} 2>&1
       """
       

rule makeblastdb:
    input:
        TF_protein = f"{config['workdir']}/jarspar/{config['jarspar_type']}/jarspar_tf_protein_sequence.fasta",
    output:
        protein_db = multiext(f"{config['workdir']}/protein_db/jarspar_tf_protein_db", ".pdb", ".phr", ".pin", ".pjs", ".pot", ".psq", ".ptf", ".pto"),
    log:
        f"{config['workdir']}/log/makeblastdb.log",
    params:
        workdir = f"{config['workdir']}/protein_db/jarspar_tf_protein_db",
        makeblastdb = config['makeblastdb']
    shell:
        """
        {params.makeblastdb} -in {input.TF_protein} -dbtype prot -out {params.workdir} 1> {log} 2>&1
        """

rule blastp:
    input:
        # protein_db_file指出了数据库中的文件的，就是说做这一步之前需要先建库且文件没有丢失，protein_db_file并没有在shell中使用
        protein_db_file = multiext(f"{config['workdir']}/protein_db/jarspar_tf_protein_db", ".pdb", ".phr", ".pin", ".pjs", ".pot", ".psq", ".ptf", ".pto"),
        
        protein = config['pep'],
    output:
        blastp_out = f"{config['workdir']}/blast/pep_blastout.xls",
        blastp_out_sort_gene_in_genome = f"{config['workdir']}/blast/pep_blastout_sort_gene_in_genome.xls",
        blastp_out_sort_jarspar_tf = f"{config['workdir']}/blast/pep_blastout_sort_jarspar_tf.xls",
    log:
        f"{config['workdir']}/log/blastp.log",
    params:
        blastp = config['blastp'],
        threads = config['blastp_threads'],
        protein_db = f"{config['workdir']}/protein_db/jarspar_tf_protein_db",
    shell:
        """
        {params.blastp} -query {input.protein} -db {params.protein_db} -num_threads {params.threads} -evalue 1e-5 -outfmt '6 std qlen slen' -out {output.blastp_out} 1> {log} 2>&1
        sort -k 2,2 {output.blastp_out} >{output.blastp_out_sort_jarspar_tf}
        sort -k 1,1 {output.blastp_out} >{output.blastp_out_sort_gene_in_genome}
        """

rule find_target_tf_in_genome:
    input:
        blastp_out_sort_jarspar_tf = f"{config['workdir']}/blast/pep_blastout_sort_jarspar_tf.xls",
        target_tf = config['target_tf']
    output:
        target_tf_in_genome = f"{config['workdir']}/target_tf_in_genome/target_tf_in_genome_blastout.xls",
    log:
        f"{config['workdir']}/log/find_target_tf_in_genome.log",
    params:
        python = config['python'],
    shell:
        """
        {params.python} {SOFTWARE_HOME}/script/find_target_tf_in_genome.py --blast {input.blastp_out_sort_jarspar_tf} --target_tf {input.target_tf} --outfile {output.target_tf_in_genome} 1> {log} 2>&1
        """





