import re

from spec2scl import settings
from spec2scl import transformer
from spec2scl.decorators import matches


@transformer.Transformer.register_transformer
class EclipseTransformer(transformer.Transformer):
    def __init__(self, options={}):
        super(EclipseTransformer, self).__init__(options)

    @matches(r'^', one_line=False, sections=['%header'])
    def eclipse_insert_scl_init(self, original_spec, pattern, text):
        scl_init = '%{{?scl:%scl_package {0}}}\n%{{!?scl:%global pkg_name %{{name}}}}\n%{{?java_common_find_provides_and_requires}}\n'.format(self.get_original_name(original_spec))
        return '{0}\n%global baserelease 0\n\n{1}'.format(scl_init, text)

    @matches(r'^Release:', one_line=True, sections=settings.METAINFO_SECTIONS)
    def eclipse_insert_baserelease(self, original_spec, pattern, text):
        return text.replace('%{?dist}', '.%{baserelease}%{?dist}', 1)

    @matches(r'brp-python-bytecompile', one_line=True, sections=['%header'])
    def python_byte_compiling(self, original_spec, pattern, text):
        return text.replace('brp-python-bytecompile', 'brp-scl-python-bytecompile', 1)
