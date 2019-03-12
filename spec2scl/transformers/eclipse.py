import re
import os

from spec2scl import settings
from spec2scl import transformer
from spec2scl.decorators import matches


@transformer.Transformer.register_transformer
class EclipseTransformer(transformer.Transformer):
    def __init__(self, options={}):
        super(EclipseTransformer, self).__init__(options)

    @matches(r'^', one_line=False, sections=['%header'])
    def eclipse_insert_scl_init(self, original_spec, pattern, text):
        scl_init = '%{{?scl:%scl_package {0}}}\n%{{!?scl:%global pkg_name %{{name}}}}\n'.format(self.get_original_name(original_spec))
        return '{0}\n%global baserelease 0\n\n{1}'.format(scl_init, text)

    @matches(r'^Release:', one_line=True, sections=settings.METAINFO_SECTIONS)
    def eclipse_insert_baserelease(self, original_spec, pattern, text):
        return text.replace('%{?dist}', '.%{baserelease}%{?dist}', 1)

    @matches(r'^(%global xmvn_libdir\s*)%\((.*)\)', one_line=True, sections=['%header'])
    def xmvn_libdir(self, original_spec, pattern, text):
        return pattern.sub(r"\1%(scl enable %{scl_maven} '\2')", text)

    @matches(r'brp-python-bytecompile', one_line=True, sections=['%header'])
    def python_byte_compiling(self, original_spec, pattern, text):
        return text.replace('brp-python-bytecompile', 'brp-scl-python-bytecompile', 1)

    @matches(r'(Recommends:\s*)(?!\w*/\w*)([^\s]+)', sections=settings.METAINFO_SECTIONS)
    @matches(r'(Enhances:\s*)(?!\w*/\w*)([^\s]+)', sections=settings.METAINFO_SECTIONS)
    def eclipse_ignore_new_tags(self, original_spec, pattern, text):
        return ''

    @matches(r'.*', one_line=False, sections=['%header'])
    def eclipse_patches_header(self, original_spec, pattern, text):
        lines = text.splitlines()
        linenum = 0
        last_occurance = -1
        for l in lines:
            if l.startswith('Source') or l.startswith('Patch'):
                last_occurance = linenum
            linenum = linenum + 1

        if os.path.isdir(self.options['patches']):
            newText = "\n# SCL-specific patches"
            files = os.listdir(self.options['patches'])
            files.sort()
            for x in range(len(files)):
                newText = newText + "\nPatch{0}: {1}".format(100 + x, files[x])

            lines.insert(last_occurance + 1, newText)
        return "\n".join(lines)
 
    @matches(r'.*', one_line=False, sections=['%prep'])
    def eclipse_patches_prep(self, original_spec, pattern, text):
        lines = text.splitlines()
        linenum = 0
        last_occurance = -1
        for l in lines:
            if l.startswith('%setup') or l.startswith('%patch'):
                last_occurance = linenum
            linenum = linenum + 1

        if os.path.isdir(self.options['patches']):
            newText = "\n# SCL-specific patches"
            files = os.listdir(self.options['patches'])
            files.sort()
            for x in range(len(files)):
                newText = newText + "\n%patch{0} -p1".format(100 + x)

            lines.insert(last_occurance + 1, newText)
        return "\n".join(lines)

    @matches(r'(Conflicts:\s*)(?!\w*/\w*)([^\s]+)', sections=settings.METAINFO_SECTIONS)
    @matches(r'(Obsoletes:\s*)(?!\w*/\w*)([^\s]+)', sections=settings.METAINFO_SECTIONS)
    @matches(r'(Provides:\s*)(?!\w*/\w*)([^\s]+)', sections=settings.METAINFO_SECTIONS)
    def eclipse_provides_obsoletes(self, original_spec, pattern, text):
        tag = text[0:text.find(':') + 1]
        provs = text[text.find(':') + 1:]
        # handle more Provides on one line

        def handle_one_prov(matchobj):
            groupdict = matchobj.groupdict('')
            provide = groupdict['dep']
            # prefix with scl name unless they begin with %{name} (in which case they are already prefixed)
            if not provide.startswith('%{name}'):
                provide = '%{{?scl_prefix}}{0}'.format(provide)
            return '{0}{1}{2}{3}'.format(groupdict['prespace'], provide, groupdict['ver'], groupdict['postspace'])

        prov_re = re.compile(r'(?P<prespace>\s*)(?P<dep>([^\s,]+(.+\))?))(?P<ver>\s*[<>=!]+\s*[^\s]+)?(?P<postspace>,?\s*)')
        new_prov = prov_re.sub(handle_one_prov, provs)
        if new_prov:
            return tag + new_prov
        else:
            return ''

    @matches(r'replace_platform_plugins_with_symlinks', one_line=True, sections=settings.BUILD_SECTIONS)
    def eclipse_replace_platform_plugins_with_symlinks(self, original_spec, pattern, text):
        return text + ' %{_javadir_maven} %{_jnidir_maven}'

