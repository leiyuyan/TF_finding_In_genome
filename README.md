# Snakefile for TF finding

- Snakefile for TF finding
- Author: Leiyu Yan
- Date: 2024-04-25
- Version: 1.0
- Description: This Snakefile is used to find TF of jarspar in protein sequences provided by user.
- Usage: snakemake --cores 16
- Output: the jarspar TF in protein sequences information，the jarspar TFs protein sequence that have uniprot id
- Input: protein.fasta,jarspar's meme file,the cared TF list file

- workdir
	- Version 1.0
		- `/data03/home/yanleiyu/24_population/08_dongxu_ZNX_FZX_LcVIN_promoter_search/fimo/TF_finding_In_protein/`
- nead to prepare github
	- ``?