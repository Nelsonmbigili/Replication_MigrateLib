from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from sympy.physics.units import frequency

from libmig_eval.util.gsheet import read_gsheet
from libmig_eval.util.models import LibPair


@dataclass
class LibPairCandidate:
    """The properties should match the columns in the spreadsheet."""
    pair_id: str
    source: str
    target: str
    frequency: int
    source_description: str
    target_description: str
    similarity: float
    target_last_release: datetime
    source_url: str
    target_url: str
    decision: str
    comment: str

    def __post_init__(self):
        self.frequency = int(self.frequency)
        sim = str(self.similarity)
        if sim.endswith("%"):
            sim = sim[:-1]
            sim = float(sim) / 100
        self.similarity = float(sim)
        self.target_last_release = datetime.strptime(str(self.target_last_release), "%Y-%m-%d")


class LibPairDb:
    def __init__(self):
        self._load_lib_pairs()

    def has_source(self, lib: str):
        return lib in self._source_libs

    def source_libs(self):
        return self._source_libs

    def target_libs(self):
        return self._target_libs

    def pairs_with_source(self, lib: str):
        return self._source_index[lib]

    def all_analogous(self):
        return self._all_analogous

    def all_candidates(self):
        return self._all_candidates

    def candidate_category(self, category: str):
        return self._candidate_categories[category]

    def _load_lib_pairs(self):
        from libmig_eval.secrets import SECRETS
        raw_lib_pairs = read_gsheet(SECRETS.validation_gsheet["file"], SECRETS.validation_gsheet["lib_pairs_sheet"])
        candidates = [LibPairCandidate(**r) for r in raw_lib_pairs]
        raw_known_lib_pairs = []  # load from google sheet

        source_libs = set()
        target_libs = set()

        candidate_categories = {
            "low_frequency": [],
            "target_old": [],
            "non_analogous": [],
            "analogous": [],
        }

        for candidate in candidates:
            if candidate.frequency < 10:
                candidate_categories["low_frequency"].append(candidate)
            elif candidate.target_last_release < datetime(2024, 1, 1):
                candidate_categories["target_old"].append(candidate)
            else:
                if candidate.decision == "analogous":
                    candidate_categories["analogous"].append(candidate)
                elif candidate.decision in {"non analogous", "not migratable - CLI only", "not testable",
                                            "documentation tool", "test library"}:
                    candidate_categories["non_analogous"].append(candidate)
                else:
                    raise ValueError(f"Unknown decision {candidate.decision or 'None'} for {candidate.pair_id}")

        self._source_index: dict[str, list[LibPair]] = defaultdict(list)
        all_analogous = []
        for candidate in candidate_categories["analogous"]:
            pair = LibPair(candidate.source, candidate.target)
            source_libs.add(pair.source)
            target_libs.add(pair.target)
            all_analogous.append(pair)
            self._source_index[pair.source].append(pair)

        self._source_libs = source_libs
        self._target_libs = target_libs
        self._all_analogous = all_analogous
        self._all_candidates = candidates
        self._candidate_categories = candidate_categories
