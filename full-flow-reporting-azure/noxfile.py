import nox


@nox.session(name="dev", python="3.10")
def dev(session):
    session.install("-r", "requirements-dev.txt")
    # session.run("python", "-m", "pip", "freeze", ">" "requirements.txt")
