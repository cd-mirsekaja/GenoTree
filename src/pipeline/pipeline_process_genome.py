from typing import Callable

import pyhmmer
import os

from src.types.genome import Genome
from src.types.gene import Alignment

class ProcessGenome:
	def __init__(self, genome: Genome, genes: list[Alignment], wdir: str | os.PathLike = os.getcwd(), log: Callable = print) -> None:
		self.log = log
		self.genome = genome
		self.genes = genes
		# change working directory
		os.chdir(wdir)
		# make directory for nhmmer tables
		os.mkdir(f"nhmmer-tables/{self.genome.accession}-tables")
	
	def runHMMER(self):
		# help: https://pyhmmer.readthedocs.io/en/stable/examples/active_site.html
		for gene in self.genes:
			with gene.hmm_path as hmm_file:
				hmm = hmm_file.read()
			
			with gene.alignment_path as seq_file:
				sequences = seq_file.read_block()
			
			