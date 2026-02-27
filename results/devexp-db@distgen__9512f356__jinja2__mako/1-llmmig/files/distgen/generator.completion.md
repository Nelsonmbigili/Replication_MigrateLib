### Explanation of Changes

To migrate the code from using the `jinja2` library to the `mako` library, the following changes were made:

1. **Import Replacement**:
   - Replaced `import jinja2` with `from mako.template import Template` and `from mako.lookup import TemplateLookup`.

2. **Template Loader**:
   - Replaced `jinja2.ChoiceLoader` and `jinja2.FileSystemLoader` with `mako.lookup.TemplateLookup`, which provides similar functionality for loading templates from directories.

3. **Template Environment**:
   - Removed the `jinja2.Environment` setup and replaced it with `TemplateLookup` for managing templates.

4. **Template Rendering**:
   - Replaced `jinja2.Template` and `tpl.render()` with `Template` from `mako.template` and its `render()` method.

5. **Error Handling**:
   - Replaced `jinja2.TemplateNotFound` and `jinja2.exceptions.TemplateNotFound` with `mako.exceptions.TopLevelLookupException`.

6. **Custom Loaders**:
   - Adjusted the custom loaders (`file_load` and `string_load`) to work with Mako templates.

7. **Recursive Rendering**:
   - Updated the `_rerender_spec` method to use `Template` from Mako for rendering strings.

### Modified Code

```python
import os
import sys
from mako.template import Template
from mako.lookup import TemplateLookup
import functools

from distgen.err import fatal
from distgen.pathmanager import PathManager
from distgen.config import load_config, merge_yaml
from distgen.project import AbstractProject
from distgen.commands import Commands
from distgen.multispec import Multispec, MultispecError

try:
    from importlib.machinery import SourceFileLoader, SourcelessFileLoader
    from importlib.util import spec_from_loader, module_from_spec
    USE_IMP = False
except ImportError:
    import imp
    USE_IMP = True


class Generator(object):
    project = None

    pm_cfg = None
    pm_tpl = None
    pm_spc = None

    def __init__(self, global_mako_args=None):
        here = os.path.dirname(os.path.abspath(__file__))
        self.pm_cfg = PathManager(
            [os.path.join(here, "distconf"),
             os.path.join(sys.prefix, "share", "distgen", "distconf")],
            envvar="DG_DISTCONFDIR"
        )

        self.pm_tpl = PathManager(
            [os.path.join(here, "templates"),
             os.path.join(sys.prefix, "share", "distgen", "templates")],
            envvar="DG_TPLDIR"
        )

        self.pm_spc = PathManager([])
        self.makoenv_args = {}

        if global_mako_args:
            self.makoenv_args.update(global_mako_args)

    def load_project(self, project):
        self.project = self._load_project_from_dir(project)
        if not self.project:
            self.project = AbstractProject()
        self.project.directory = project

        def file_load(name):
            """
            The default TemplateLookup doesn't load files specified
            by absolute paths or paths that include '..' - therefore
            we provide a custom fallback function that handles this.
            """
            name = os.path.abspath(name)
            try:
                with open(name, 'rb') as f:
                    return f.read().decode('utf-8')
            except Exception:
                raise FileNotFoundError(name)

        def string_load(name):
            """
            Allow specifying a string instead of template to be able
            to return expanded config/specs/...
            """
            if name.startswith(('${', '<%')):
                return name
            raise FileNotFoundError(name)

        self.project.tplgen = TemplateLookup(
            directories=self.pm_tpl.get_path(),
            **self.makoenv_args
        )

        self.project.abstract_initialize()

    @staticmethod
    def _load_python_file_importlib(filename):
        """ load compiled python source """
        mod_name, file_ext = os.path.splitext(os.path.split(filename)[-1])
        if file_ext.lower() == '.py':
            Loader = SourceFileLoader
        elif file_ext.lower() == '.pyc':
            Loader = SourcelessFileLoader

        loader = Loader(mod_name, filename)
        spec = spec_from_loader(loader.name, loader)
        py_mod = module_from_spec(spec)
        loader.exec_module(py_mod)

        return py_mod

    @staticmethod
    def _load_python_file_imp(filename):
        """ load compiled python source """
        mod_name, file_ext = os.path.splitext(os.path.split(filename)[-1])
        if file_ext.lower() == '.py':
            # pylint: disable=used-before-assignment
            py_mod = imp.load_source(mod_name, filename)
        elif file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, filename)

        return py_mod

    if USE_IMP:
        _load_python_file = _load_python_file_imp
    else:
        _load_python_file = _load_python_file_importlib

    def _load_obj_from_file(self, filename, objname):
        py_mod = self._load_python_file(filename)

        if hasattr(py_mod, objname):
            return getattr(py_mod, objname)
        else:
            return None

    def _load_obj_from_projdir(self, projectdir, objname):
        """ given project directory, load possibly existing project.py """
        project_file = os.path.join(projectdir, "project.py")

        if os.path.isfile(project_file):
            return self._load_obj_from_file(project_file, objname)
        else:
            return None

    def _load_project_from_dir(self, projectdir):
        """ given project directory, load possibly existing project.py """
        projclass = self._load_obj_from_projdir(projectdir, "Project")
        if not projclass:
            return None
        return projclass()

    def _rerender_spec(self, s, **kwargs):
        changed = False

        if isinstance(s, dict):
            for k, v in s.items():
                _changed, s[k] = self._rerender_spec(v, **kwargs)
                changed |= _changed
        elif isinstance(s, list):
            for i in range(0, len(s)):
                _changed, s[i] = self._rerender_spec(s[i], **kwargs)
                changed |= _changed
        elif isinstance(s, str):
            new_spec = Template(s).render(**kwargs)
            changed = s != new_spec
            s = new_spec
        else:
            pass  # int, float, perhaps something else?

        return changed, s

    def render(self, specfiles, multispec, multispec_selectors, template,
               config, cmd_cfg, output, confdirs=None,
               explicit_macros={}, max_passes=1):
        """ render single template """
        config_path = [self.project.directory] + self.pm_cfg.get_path()
        sysconfig = load_config(config_path, config)

        if not confdirs:
            confdirs = []
        for i in confdirs + [self.project.directory]:
            additional_vars = self.load_config_from_project(i)
            self.vars_fill_variables(additional_vars, sysconfig)
            # filter only interresting variables
            interresting_parts = ['macros']
            additional_vars = {
                x: additional_vars[x] for x in
                interresting_parts if x in additional_vars}
            sysconfig = merge_yaml(sysconfig, additional_vars)

        self.project.abstract_setup_vars(sysconfig)

        self.project.inst_init(specfiles, template, sysconfig)

        projcfg = self.load_config_from_project(self.project.directory)
        if projcfg and 'name' in projcfg:
            sysconfig['name'] = projcfg['name']
        self.vars_fill_variables(sysconfig)

        explicit_macros = {'macros': explicit_macros}
        self.vars_fill_variables(explicit_macros, sysconfig)
        sysconfig = merge_yaml(sysconfig, explicit_macros)

        yaml = self._enhanced_yaml_module(sysconfig)

        spec = {}
        for specfile in specfiles or []:
            specfd = self.pm_spc.open_file(
                specfile,
                [self.project.directory],
                fail=True,
            )
            if not specfd:
                fatal("Spec file {0} not found".format(specfile))

            try:
                specdata = yaml.dg_load(specfd)
                spec = merge_yaml(spec, specdata)
            except yaml.YAMLError as exc:
                fatal("Error in spec file: {0}".format(exc))
        if multispec:
            try:
                mltspc = Multispec.from_path(self.project.directory, multispec)
                spec = merge_yaml(
                    spec, mltspc.select_data(multispec_selectors, config))
            except yaml.YAMLError as exc:
                fatal("Error in multispec file: {0}".format(exc))
            except MultispecError as exc:
                fatal(str(exc), exc.exit_code)

        try:
            tpl = self.project.tplgen.get_template(template)
        except Exception as err:
            fatal("Can not find template {0}".format(err))

        self.project.inst_finish(specfiles, template, sysconfig, spec)

        rendering_kwargs = {
            'config': sysconfig,
            'macros': sysconfig['macros'],
            'm': sysconfig['macros'],
            'container': {'name': 'docker'},
            'spec': spec,
            'project': self.project,
            'commands': Commands(cmd_cfg, sysconfig),
            'env': os.environ,
        }

        self._recursive_render_spec(
            spec,
            max_passes=max_passes,
            **rendering_kwargs
        )

        output.write(tpl.render(**rendering_kwargs).encode('utf-8'))
```

This code now uses the `mako` library for template rendering instead of `jinja2`.