from glob import glob

import nox

REPO_TOOLS_REQ = \
    'git+https://github.com/GoogleCloudPlatform/python-repo-tools.git'

DIRS = [
    # Hello world doesn't have system tests, just a lint test which will be
    # covered by the global lint here.
    # '1-hello-world',
    '2-structured-data',
    '3-binary-data',
    '4-auth',
    '5-logging',
    '6-pubsub',
    '7-gce',
    'optional-kubernetes-engine'
]


@nox.session
def check_requirements(session):
    session.install(REPO_TOOLS_REQ)

    if 'update' in session.posargs:
        command = 'update-requirements'
    else:
        command = 'check-requirements'

    for reqfile in glob('**/requirements*.txt'):
        session.run('gcp-devrel-py-tools', command, reqfile)


@nox.session
def lint(session):
    session.install('flake8', 'flake8-import-order')
    session.run(
        'flake8', '--exclude=env,.nox,._config.py,.tox',
        '--import-order-style=google', '.')


def run_test(session, dir, toxargs):
    session.chdir(dir)
    session.install('tox')
    session.run('tox', *(toxargs or []))


@nox.session
@nox.parametrize('dir', DIRS)
def run_tests(session, dir=None, toxargs=None):
    """Run all tests for all directories (slow!)"""
    run_test(session, dir, toxargs)


@nox.session
@nox.parametrize('dir', DIRS)
def travis(session, dir=None):
    """On travis, only run lint."""
    run_tests(
        session,
        dir=dir,
        toxargs=['-e', 'lint'])
