from libmig.project import Project


def install_project_venv(project: Project):
    log = project.get_loger()
    venv = project.venv
    required_scripts = ["python", "pytest", "coverage", "pip", "pprofile"]

    if not all(venv.script(script).exists() for script in required_scripts):
        # some scripts are missing. venv needs to be created
        log.log_event(f"creating venv at {venv.venv_dir.as_posix()}")
        venv.venv_dir.mkdir(parents=True, exist_ok=True)
        #venv.venv_dir.joinpath(".gitignore").write_text("*\n")
        venv.create()

    log.log_event(f"installing dependencies")
    for req_path in project.requirements_file_paths:
        venv.run_script("pip", "install", "-r", req_path.as_posix())
    venv.run_script("pip", "install", "pytest", "pytest-cov", "pytest-json-report", "pytest-html", "pprofile",
                    "setuptools")
    venv.run_script("pip", "install", project.code_path.as_posix())

    src_version = venv.installed_version(project.source)
    if not src_version:
        venv.install(project.source, "latest")
        src_version = venv.installed_version(project.source)

    tgt_version = venv.installed_version(project.target)
    if not tgt_version:
        venv.install(project.target, "latest")
        tgt_version = venv.installed_version(project.target)

    return src_version, tgt_version
