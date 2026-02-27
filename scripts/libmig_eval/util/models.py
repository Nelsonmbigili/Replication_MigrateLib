from dataclasses import dataclass


def encode_repo_id(repo: str, commit: str) -> str:
    return repo.replace("/", "@") + "__" + commit[:8]


def decode_repo_id(repo_id: str) -> tuple[str, str]:
    repo, commit = repo_id.split("__")
    return repo.replace("@", "/"), commit


def decode_mig_id(mig_id: str) -> tuple[str, str, str, str]:
    repo, commit, src, tgt = mig_id.split("__")
    repo = repo.replace("@", "/")
    return repo, commit, src, tgt


@dataclass(eq=True, order=True, unsafe_hash=True)
class Mig:
    id: str
    repo: str
    commit: str
    source: str
    target: str

    def __post_init__(self):
        self.repo_id = encode_repo_id(self.repo, self.commit)
        self.lib_pair = LibPair(self.source, self.target)
        self.lib_pair_id = self.lib_pair.id

    def to_dict(self):
        return {
            "id": self.id,
            "repo": self.repo,
            "commit": self.commit,
            "source": self.source,
            "target": self.target
        }


@dataclass(frozen=True, eq=True, order=True)
class LibPair:
    source: str
    target: str

    @property
    def id(self):
        return f"{self.source}__{self.target}"

    def __str__(self):
        return f"{self.source}__{self.target}"
