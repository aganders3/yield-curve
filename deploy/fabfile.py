from fabric import task

import os
import getpass

# create a new droplet if needed (-N)
# create new user (sudoer)
# copy SSH key to server, disable password

APP_NAME = 'indicator'
URL = 'market-weather.com'

USER = 'aganders3'
PUB_KEY = '~/.ssh/id_rsa.pub'

@task
def new_user(c, username=USER, pubkey_file=PUB_KEY):

    # create a new user and make it a sudoer
    new_pass = getpass.getpass("Enter a password for the new user")
    c.run('adduser --disabled-password --gecos "" {}'.format(username))
    c.run('usermod -aG sudo {}'.format(username))
    c.run('echo "{}:{}" | chpasswd'.format(username, new_pass))

    # add public key
    with open(os.path.expanduser(pubkey_file)) as fd:
        ssh_key = fd.readline().strip()

    c.run('mkdir -p -m 700 /home/{}/.ssh'.format(username))
    c.run('chown {0}:{0} /home/{0}/.ssh'.format(username))
    c.run('touch /home/{}/.ssh/authorized_keys'.format(username))
    c.run('echo "{}" >> /home/{}/.ssh/authorized_keys'.format(ssh_key, username))
    c.run('chown {0}:{0} /home/{0}/.ssh/authorized_keys'.format(username))
    c.run('chmod 600 /home/{}/.ssh/authorized_keys'.format(username))

@task
def setup(c):
    # set up UFW (firewall) to allow OpenSSH

    # install python3-pip python3-dev nginx
    c.run('apt-get update')
    c.run('apt-get install python3-pip python3-dev nginx')

    # create the working directory for the app
    c.run('pip3 install virtualenv')
    c.run('mkdir -p /var/www/{}'.format(APP_NAME))

    # set up bare git repo separate from the work directory
    c.run('mkdir -p /var/repo/{}.git'.format(APP_NAME))
    c.run('git init --bare /var/repo/{}.git'.format(APP_NAME))

    # set up post-receive hook for copying files to the work tree
    with c.cd('/var/repo/{}.git/hooks'.format(APP_NAME)):
        c.run('touch post-receive')
        c.run('chmod +x post-receive')
        c.run('echo "#!/bin/sh" >> post-receive')
        c.run(('echo "git --work-tree=/var/www/domain.com '
               '--git-dir=/var/repo/site.git checkout -f" >> post-receive'))


    # set remote for local git with server name
    c.local('git remote add live ssh://{}@{}/var/repo/{}.git'.format(c.user,
                                                                     c.host,
                                                                     APP_NAME))

    # create app virtual environment and install deps
    c.run('virtualenv /var/www/{0}/{0}_env'.format(APP_NAME))
    c.run('/var/www/{0}/{0}_env/bin/pip install flask gunicorn'.format(APP_NAME))

    # set up UFW to allow nginx

    # push up systemd startup script
    # push up initial DB
    # add any cron job(s)

    # install gunicorn and start it

    # push nginx config files, start it

    # set up SSH with Let's Encrypt





