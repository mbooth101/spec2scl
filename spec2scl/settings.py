"""Transformation related settings and constants.
"""

SPECFILE_SECTIONS = ['%header',  # special "section" for the start of specfile
                     '%description',
                     '%package',
                     '%prep',
                     '%build',
                     '%install',
                     '%clean',
                     '%check',
                     '%pre',
                     '%post',
                     '%preun',
                     '%postun',
                     '%pretrans',
                     '%posttrans',
                     '%files',
                     '%changelog']

RUNTIME_SECTIONS = ['%prep', '%build', '%install', '%clean', '%check', '%pre', '%post', '%preun', '%postun', '%pretrans', '%posttrans']
BUILD_SECTIONS = ['%prep', '%build', '%install', '%clean', '%check']
METAINFO_SECTIONS = ['%header', '%package']

SCL_ENABLE = '%{?scl:scl enable %{scl_maven} %{scl} - << "EOFSCL"}\nset -e -x\n'
SCL_DISABLE = '%{?scl:EOFSCL}\n'
