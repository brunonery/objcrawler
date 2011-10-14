from fabric.api import cd, local, put, run

def build():
    # Create build tree.
    local('mkdir -p build/')
    local('mkdir -p build/config/')
    local('mkdir -p build/data/')
    # Freeze binaries.
    local('bb-freeze src/seeder/seeder.py')
    # Put frozen binaries and dependencies in the build tree.
    local('mv dist/ build/bin/')
    # Copy configuration files.
    local('cp config/* build/config/')
    # TODO(brunonery): generate scripts to start/stop all services.
    # Create installation tarball.
    local('tar cjf objcrawler.tbz2 build/')
    # Remove build tree.
    local('rm -rf build/')

def clean():
    local('find . -name "*.pyc" | xargs rm')
    local('rm objcrawler.tbz2')

def deploy():
    run('mkdir -p objcrawler/')
    with cd('objcrawler'):
        put('objcrawler.tbz2', '.')
        run('tar xjf objcrawler.tbz2')

def test():
    local('nosetests')
