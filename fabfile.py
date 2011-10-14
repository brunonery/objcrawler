from fabric.api import local

def clean():
    local('find . -name "*.pyc" | xargs rm')

def test():
    local('nosetests')

