from itertools import cycle

import yaml

from libmig_eval.util.paths import Paths


class _Secrets:
    def __init__(self):
        paths = Paths()
        raw_secrets = yaml.safe_load((paths.eval_project_root / "secrets/secrets.yaml").open("r"))
        self.libio_api_key = raw_secrets["LIBIO_API_KEY"]
        self._github_access_tokens = cycle(raw_secrets["GITHUB_ACCESS_TOKENS"])
        self.openai_api_key = raw_secrets["OPENAI_API_KEY"]
        self.validation_gsheet: dict[str, str] = raw_secrets["VALIDATION_GSHEET"]
        self.repo_root= raw_secrets.get("REPO_ROOT", None)

    @property
    def github_access_token(self):
        return next(self._github_access_tokens)


SECRETS = _Secrets()
