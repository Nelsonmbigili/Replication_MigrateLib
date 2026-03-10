## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/devexp-db@distgen__9512f356__jinja2__mako/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating distgen/generator.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_cleancache[dnfi-dnf clean all --enablerepo='*']: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_cleancache[dnfni-dnf -y clean all --enablerepo='*']: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_cleancache[yumi-yum clean all --enablerepo='*']: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_cleancache[yumni-yum -y clean all --enablerepo='*']: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[dnfi-install-dnf install foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[dnfi-reinstall-dnf reinstall foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[dnfi-remove-dnf remove foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[dnfi-update-dnf update foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[dnfni-install-dnf -y install foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[dnfni-reinstall-dnf -y reinstall foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[dnfni-remove-dnf -y remove foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[dnfni-update-dnf -y update foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[yumi-install-yum install foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[yumi-reinstall-yum reinstall foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[yumi-remove-yum remove foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[yumi-update-yum update foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[yumni-install-yum -y install foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[yumni-reinstall-yum -y reinstall foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[yumni-remove-yum -y remove foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_pkg_methods[yumni-update-yum -y update foo bar]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_update_all[dnfi-dnf update]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_update_all[dnfni-dnf -y update]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_update_all[yumi-yum update]: passed != not found`
- `tests/unittests/test_commands.py::TestIndividualPkgManagers::test_update_all[yumni-yum -y update]: passed != not found`
- `tests/unittests/test_config.py::TestLoadConfig::test_recursive: passed != not found`
- `tests/unittests/test_config.py::TestLoadConfig::test_simple: passed != not found`
- `tests/unittests/test_config.py::TestMergeYaml::test_nested: passed != not found`
- `tests/unittests/test_config.py::TestMergeYaml::test_non_overlapping: passed != not found`
- `tests/unittests/test_config.py::TestMergeYaml::test_overlapping: passed != not found`
- `tests/unittests/test_distro_detection.py::TestDistroDetection::test_others: passed != not found`
- `tests/unittests/test_distro_detection.py::TestDistroDetection::test_rpm[fedora-21-rawhide-rawhide-i386]: passed != not found`
- `tests/unittests/test_distro_detection.py::TestDistroDetection::test_rpm[fedora-21-rawhide-rawhide-x86_64]: passed != not found`
- `tests/unittests/test_distro_detection.py::TestDistroDetection::test_rpm[fedora-24-sth-24-i386]: passed != not found`
- `tests/unittests/test_distro_detection.py::TestDistroDetection::test_rpm[fedora-24-sth-24-x86_64]: passed != not found`
- `tests/unittests/test_distro_detection.py::TestDistroDetection::test_rpm[fedora-25-sth-25-i386]: passed != not found`
- `tests/unittests/test_distro_detection.py::TestDistroDetection::test_rpm[fedora-25-sth-25-x86_64]: passed != not found`
- `tests/unittests/test_distro_detection.py::TestDistroDetection::test_rpm[rhel-7-sth-7-i386]: passed != not found`
- `tests/unittests/test_distro_detection.py::TestDistroDetection::test_rpm[rhel-7-sth-7-x86_64]: passed != not found`
- `tests/unittests/test_error.py::TestFatal::test_fatal: passed != not found`
- `tests/unittests/test_error.py::TestFatal::test_fatal_custom_exit_code: passed != not found`
- `tests/unittests/test_generator.py::TestGenerator::test_fill_variables[config0-None-result0]: passed != not found`
- `tests/unittests/test_generator.py::TestGenerator::test_fill_variables[config1-sysconfig1-result1]: passed != not found`
- `tests/unittests/test_generator.py::TestGenerator::test_load_project[projectfile-bar]: passed != not found`
- `tests/unittests/test_generator.py::TestGenerator::test_render[/Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/devexp-db@distgen__9512f356__jinja2__mako/tests/unittests/fixtures/generator/simple-/Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/devexp-db@distgen__9512f356__jinja2__mako/tests/unittests/fixtures/generator/simple/Dockerfile-10-FROM fedora:26\n\nLABEL MAINTAINER ...\n\nENV NAME=mycontainer VERSION=0 RELEASE=1 ARCH=x86_64\n\nLABEL summary="A container that tells you how awesome it is." \\n      com.redhat.component="$NAME" \\n      version="$VERSION" \\n      release="$RELEASE.$DISTTAG" \\n      architecture="$ARCH" \\n      usage="docker run -p 9000:9000 mycontainer" \\n      help="Runs mycontainer, which listens on port 9000 and tells you how awesome it is. No dependencies." \\n      description="This is a simple container that just tells you how awesome it is. That's it." \\n      vendor="Fedora Project" \\n      org.fedoraproject.component="postfix" \\n      authoritative-source-url="some.url.fedoraproject.org" \\n      io.k8s.description="This is a simple container that just tells you how awesome it is. That's it." \\n      io.k8s.display-name="Awesome container with SW version " \\n      io.openshift.expose-services="9000:http" \\n      io.openshift.tags="some,tags"\n\nEXPOSE 9000\n\n# We don't actually use the "software_version" here, but we could,\n#  e.g. to install a module with that ncat version\nRUN dnf -y install nmap-ncat && \\n    dnf -y clean all --enablerepo='*'\n\nRUN echo ham fedora 2.4\nRUN echo 2.4\n\n# add help file\n#  NOTE: this file is rendered from help.md, it's not actually templated (help.md is)\nCOPY root/help.1 /\nCOPY script.sh /usr/bin/\n\nCMD ["/usr/bin/script.sh"]\n]: passed != not found`
- `tests/unittests/test_generator.py::TestGenerator::test_render[/Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/devexp-db@distgen__9512f356__jinja2__mako/tests/unittests/fixtures/generator/simple-/Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/devexp-db@distgen__9512f356__jinja2__mako/tests/unittests/fixtures/generator/simple/Dockerfile-2-FROM fedora:26\n\nLABEL MAINTAINER ...\n\nENV NAME=mycontainer VERSION=0 RELEASE=1 ARCH=x86_64\n\nLABEL summary="A container that tells you how awesome it is." \\n      com.redhat.component="$NAME" \\n      version="$VERSION" \\n      release="$RELEASE.$DISTTAG" \\n      architecture="$ARCH" \\n      usage="docker run -p 9000:9000 mycontainer" \\n      help="Runs mycontainer, which listens on port 9000 and tells you how awesome it is. No dependencies." \\n      description="This is a simple container that just tells you how awesome it is. That's it." \\n      vendor="Fedora Project" \\n      org.fedoraproject.component="postfix" \\n      authoritative-source-url="some.url.fedoraproject.org" \\n      io.k8s.description="This is a simple container that just tells you how awesome it is. That's it." \\n      io.k8s.display-name="Awesome container with SW version " \\n      io.openshift.expose-services="9000:http" \\n      io.openshift.tags="some,tags"\n\nEXPOSE 9000\n\n# We don't actually use the "software_version" here, but we could,\n#  e.g. to install a module with that ncat version\nRUN dnf -y install nmap-ncat && \\n    dnf -y clean all --enablerepo='*'\n\nRUN echo ham fedora 2.4\nRUN echo 2.4\n\n# add help file\n#  NOTE: this file is rendered from help.md, it's not actually templated (help.md is)\nCOPY root/help.1 /\nCOPY script.sh /usr/bin/\n\nCMD ["/usr/bin/script.sh"]\n]: passed != not found`
- `tests/unittests/test_generator.py::TestGenerator::test_render[/Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/devexp-db@distgen__9512f356__jinja2__mako/tests/unittests/fixtures/generator/simple-{{ config.os.id }}-2-fedora]: passed != not found`
- `tests/unittests/test_generator.py::TestGenerator::test_render[/Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/devexp-db@distgen__9512f356__jinja2__mako/tests/unittests/fixtures/generator/simple_with_projectfile-/Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/devexp-db@distgen__9512f356__jinja2__mako/tests/unittests/fixtures/generator/simple_with_projectfile/Dockerfile-10-FROM fedora:26\n\nLABEL MAINTAINER ...\n\nENV NAME=mycontainer VERSION=0 RELEASE=1 ARCH=x86_64\n\nLABEL summary="A container that tells you how awesome it is." \\n      com.redhat.component="$NAME" \\n      version="$VERSION" \\n      release="$RELEASE.$DISTTAG" \\n      architecture="$ARCH" \\n      usage="docker run -p 9000:9000 mycontainer" \\n      help="Runs mycontainer, which listens on port 9000 and tells you how awesome it is. No dependencies." \\n      description="This is a simple container that just tells you how awesome it is. That's it." \\n      vendor="Fedora Project" \\n      org.fedoraproject.component="postfix" \\n      authoritative-source-url="some.url.fedoraproject.org" \\n      io.k8s.description="This is a simple container that just tells you how awesome it is. That's it." \\n      io.k8s.display-name="Awesome container with SW version " \\n      io.openshift.expose-services="9000:http" \\n      io.openshift.tags="some,tags"\n\nEXPOSE 9000\n\n# We don't actually use the "software_version" here, but we could,\n#  e.g. to install a module with that ncat version\nRUN dnf -y install nmap-ncat && \\n    dnf -y clean all --enablerepo='*'\n\nRUN echo interesting\nRUN echo ham\nRUN echo 2.4\n\n# add help file\n#  NOTE: this file is rendered from help.md, it's not actually templated (help.md is)\nCOPY root/help.1 /\nCOPY script.sh /usr/bin/\n\nCMD ["/usr/bin/script.sh"]\n]: passed != not found`
- `tests/unittests/test_generator.py::TestGenerator::test_vars_fixed_point[config0-result0]: passed != not found`
- `tests/unittests/test_generator.py::TestGenerator::test_vars_fixed_point[config1-result1]: passed != not found`
- `tests/unittests/test_generator.py::TestGenerator::test_vars_fixed_point[config2-result2]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_distrofile2name: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_from_path_nok: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_from_path_ok[/Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/devexp-db@distgen__9512f356__jinja2__mako/tests/unittests/fixtures-multispec/simplest.yaml]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_from_path_ok[/Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/devexp-db@distgen__9512f356__jinja2__mako/tests/unittests/fixtures/multispec-simplest.yaml]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_get_all_combinations_complex: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_get_all_combinations_simple: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_get_extras[centos-7-x86_64-selectors2-expected2]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_get_extras[fedora-26-x86_64-selectors0-expected0]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_get_extras[fedora-26-x86_64-selectors1-expected1]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_get_spec_group: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_get_spec_group_item: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_has_spec_group: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_has_spec_group_item: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_is_combination_in_matrix_exclude[exclude-fedora-25-x86_64-selectors2-False]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_is_combination_in_matrix_exclude[exclude-fedora-25-x86_64-selectors3-True]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_is_combination_in_matrix_exclude[exclude-fedora-26-x86_64-selectors0-True]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_is_combination_in_matrix_exclude[exclude-fedora-26-x86_64-selectors1-False]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_is_combination_in_matrix_include[include-fedora-25-x86_64-selectors2-False]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_is_combination_in_matrix_include[include-fedora-25-x86_64-selectors3-True]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_is_combination_in_matrix_include[include-fedora-26-x86_64-selectors0-True]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_is_combination_in_matrix_include[include-fedora-26-x86_64-selectors1-False]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_parse_selectors_nok: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_parse_selectors_ok: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_select_data_nok: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_select_data_ok: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_validate: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_include_and_exclude: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_nok[selectors0-fedora-26-x86_64-"distroinfo" not allowed in selectors, it is chosen automatically based on distro]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_nok[selectors1-fedora-26-x86_64-"something_else" selector must be present]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_nok[selectors2-fedora-26-x86_64-"xxx" not an entry in specs]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_nok[selectors3-fedora-26-x86_64-"3.4" not an entry in specs.version]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_nok[selectors4-fedora-26-x86_64-This combination is excluded in matrix section]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_nok[selectors5-fedora-27-x86_64-"fedora-27-x86_64" distro not found in any specs.distroinfo.*.distros section]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_nok_not_included[selectors0-fedora-26-x86_64-This combination is not included in matrix section]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_nok_not_included[selectors1-fedora-26-x86_64-This combination is not included in matrix section]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_nok_not_included[selectors2-fedora-25-x86_64-This combination is not included in matrix section]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_nok_not_included[selectors3-fedora-25-x86_64-This combination is not included in matrix section]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_ok_exclude[fedora-25-x86_64-selectors1]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_ok_exclude[fedora-25-x86_64-selectors3]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_ok_exclude[fedora-26-x86_64-selectors0]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_ok_exclude[fedora-26-x86_64-selectors2]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_ok_include[fedora-25-x86_64-selectors1]: passed != not found`
- `tests/unittests/test_multispec.py::TestMultispec::test_verify_selectors_ok_include[fedora-26-x86_64-selectors0]: passed != not found`
- `tests/unittests/test_pathmanager.py::TestPathmanager::test_get_file_abspath: passed != not found`
- `tests/unittests/test_pathmanager.py::TestPathmanager::test_get_file_relpath[path0-None-False-NoneType]: passed != not found`
- `tests/unittests/test_pathmanager.py::TestPathmanager::test_get_file_relpath[path1-None-False-TextIOWrapper]: passed != not found`
- `tests/unittests/test_pathmanager.py::TestPathmanager::test_get_file_relpath[path2-None-False-TextIOWrapper]: passed != not found`
- `tests/unittests/test_pathmanager.py::TestPathmanager::test_get_file_relpath[path3-prefered_path3-False-TextIOWrapper]: passed != not found`
- `tests/unittests/test_pathmanager.py::TestPathmanager::test_get_file_relpath[path4-None-True-retval4]: passed != not found`
- `tests/unittests/test_pathmanager.py::TestPathmanager::test_get_path: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
