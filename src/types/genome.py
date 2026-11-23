import os
from dataclasses import dataclass

@dataclass
class Genome:
	accession: str
	scientific_name: str
	genome_path: str | os.PathLike