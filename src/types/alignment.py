import os
from dataclasses import dataclass

@dataclass
class Alignment:
	name: str
	alignment_path: str | os.PathLike
	hmm_path: str | os.PathLike = ""