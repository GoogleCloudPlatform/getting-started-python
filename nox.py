from glob import glob

REPO_TOOLS_REQ =\
    'git+https://github.com/GoogleCloudPlatform/python-repo-tools.git'


def session_reqcheck(session):
    session.install(REPO_TOOLS_REQ)

    for reqfile in glob('**/requirements.txt'):
        session.run('gcprepotools', 'check-requirements', reqfile)


def session_requpdate(session):
    session.install(REPO_TOOLS_REQ)

    for reqfile in glob('**/requirements.txt'):
        session.run('gcprepotools', 'update-requirements', reqfile)
