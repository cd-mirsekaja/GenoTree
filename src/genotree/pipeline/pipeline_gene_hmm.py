import os
from typing import Callable

import pyhmmer

from types.alignment import Alignment

class GeneMM:
	def __init__(self, alignment: Alignment,
				 alphabet: pyhmmer.easel.Alphabet = pyhmmer.easel.Alphabet.amino(),
				 log: Callable = print) -> None:
		self.log = log
		self.alignment = alignment
		self.alphabet = alphabet
		self.hmm = None
		self.msa = None
	
	def build(self):
		builder = pyhmmer.plan7.Builder(self.alphabet)
		background = pyhmmer.plan7.Background(self.alphabet)
		
		with pyhmmer.easel.MSAFile(self.alignment.alignment_path, digital = True, alphabet = self.alphabet) as msa_file:
			self.msa = msa_file.read()
		
		self.msa.name = self.alignment.name
		self.hmm, _, _ = builder.build_msa(self.msa, background)
	
	def save(self):
		if not self.hmm is None:
			with open(self.alignment.hmm_path, "wb") as hmm_file:
				self.hmm.write(hmm_file)
		
			self.log(f"HMM file written to {self.alignment.hmm_path}.")
		else:
			self.log(f"No HMM cached yet for {self.alignment.name}.")
	
	def load(self):
		if not self.hmm is None:
			return self.hmm
		else:
			if not os.isfile(self.alignment.hmm_path):
				return FileNotFoundError(f"No file found at {self.alignment.hmm_path}")
		
			with open(self.alignment.hmm_path, "r") as hmm_file:
				self.hmm = hmm_file.read()
			
			return self.hmm