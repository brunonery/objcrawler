from fabric.api import local

def clean():
    local("rm *.pyc")

def test():
    local("nosetests")

