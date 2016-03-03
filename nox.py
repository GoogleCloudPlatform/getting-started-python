from glob import glob

REPO_TOOLS_REQ =\
    'git+https://github.com/GoogleCloudPlatform/python-repo-tools.git'


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
