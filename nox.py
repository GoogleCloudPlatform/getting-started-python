from glob import glob
import shutil

import nox

REPO_TOOLS_REQ = \
    'git+https://github.com/GoogleCloudPlatform/python-repo-tools.git'

DIRS = [
    '1-hello-world',
    '2-structured-data',
    '3-binary-data',
    '4-auth',
    '5-logging',
    '6-pubsub',
    '7-gce']


def session_reqcheck(session):
    session.install(REPO_TOOLS_REQ)

    if 'update' in session.posargs:
        command = 'update-requirements'
    else:
        command = 'check-requirements'

    for reqfile in glob('**/requirements.txt'):
        session.run('gcprepotools', command, reqfile)


def session_lint(session):
    session.install('flake8', 'flake8-import-order')
    session.run(
        'flake8', '--exclude=env,.nox,._config.py',
        '--import-order-style=google', '.')


def run_test(session, dir, toxargs):
    shutil.copy('config.py', dir)
    session.chdir(dir)
    session.run('tox', *(toxargs or []))


@nox.parametrize('dir', DIRS)
def session_run_tests(session, dir=None, toxargs=None):
    """Run all tests for all directories (slow!)"""
    run_test(session, dir, toxargs)


def session_run_one_test(session):
    dir = session.posargs[0]
    toxargs = session.posargs[1:]
    run_test(session, dir, toxargs)


@nox.parametrize('dir', DIRS)
def session_travis(session, dir=None):
    """On travis, only run the py3.4 and cloudsql tests."""
    if dir == '1-hello-world':
        session_run_tests(
            session, dir=dir, toxargs=['-e', 'lint'])
    else:
        shutil.copy('config.py', dir)
        session_run_tests(
            session,
            dir=dir,
            toxargs=['-e', 'py34', '--', '-k', 'cloudsql'])
