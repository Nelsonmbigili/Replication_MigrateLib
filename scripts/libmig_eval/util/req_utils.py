import requests
from libmig.utils.cache import read_cache, write_cache


def read_requirements_file_from_github(repo_name: str, commit: str, file_path: str = "requirements.txt"):
    cache_path = f"requirements/{repo_name.replace('/', '@')}__{commit}__{file_path.replace('/', '__')}"
    content = read_cache(cache_path)
    if not content:
        url = f"https://raw.githubusercontent.com/{repo_name}/{commit}/{file_path}"
        response = requests.get(url)
        if response.status_code != 200:
            return []
        content = response.text
        write_cache(cache_path, content)

    requirements = read_requirements_file(content)
    return requirements


def read_requirements_file(content: str):
    from pkg_resources import parse_requirements, Requirement

    def requirements_from_lines():
        lines = content.split("\n")
        for line in lines:
            try:
                req = Requirement.parse(line)
                yield req
            except:
                pass

    try:
        requirements = parse_requirements(content)
        return list(requirements)
    except:
        return list(requirements_from_lines())
