from fabric.api import cd, local, put, run
import sys

def build():
    # Create build tree.
    local('mkdir -p build/config/')
    local('mkdir -p build/data/models')
    # Freeze binaries.
    local('bb-freeze src/seeder/seeder.py src/crawler/crawler.py')
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
    local('rm -f objcrawler.tbz2')
    local('rm -f data/objcrawler.db')
    local('rm -rf data/models/*')
    local('rm -f test/tmp/*')

def deploy():
    run('mkdir -p objcrawler/')
    with cd('objcrawler'):
        put('objcrawler.tbz2', '.')
        run('tar xjf objcrawler.tbz2')

def test():
    clean()
    local('nosetests')

def fresh_start():
    clean()
    local('python src/seeder/seeder.py --config config/objcrawler.cfg --use_google --query "3d models"')
    local('python src/crawler/crawler.py --config config/objcrawler.cfg')
