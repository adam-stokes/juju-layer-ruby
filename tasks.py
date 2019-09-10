from invoke import task


@task
def fix(c):
    c.run("isort -rc -m 3 .")
    c.run("black .")


@task
def test(c):
    c.run("pylint reactive lib")
    c.run("flake8 .")
