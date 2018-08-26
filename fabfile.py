from fabric import task

import os
import getpass

# create a new droplet if needed (-N)

APP_NAME = 'indicator'

USER = 'aganders3'
PUB_KEY = '~/.ssh/id_rsa.pub'

@task
def adduser(c, username=USER, pubkey_file=PUB_KEY):
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
def init(c):
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
        # check out the files after a push
        c.run('echo "#!/bin/sh" >> post-receive')
        c.run(('echo "git --work-tree=/var/www/{0} '
               '--git-dir=/var/repo/{0}.git checkout -f" '
               '>> post-receive').format(APP_NAME))

    # set remote for local git with server name
    c.local('git remote add live ssh://{}@{}/var/repo/{}.git'.format(c.user,
                                                                     c.host,
                                                                     APP_NAME))

    # create app virtual environment and install deps
    c.run('virtualenv /var/www/{0}/{0}_env'.format(APP_NAME))
    # c.run('/var/www/{0}/{0}_env/bin/pip install flask gunicorn'.format(APP_NAME))

    # set up UFW to allow nginx
    # set up SSH with Let's Encrypt

@task
def update(c):
    c.local('git push live')

    # update venv
    c.run('/var/www/{0}/{0}_env/bin/pip install -r requirements.txt'.format(APP_NAME))

    # copy indicator.nginx to sites-available
    c.run('cp {0}.nginx /etc/nginx/sites-available/{0}'.format(APP_NAME))

    # copy systemd file to /etc/systemd/system/indicator.service
    c.run('cp {}.service /etc/systemd/system/'.format(APP_NAME))

    # add any cron job(s)

@task
def start(c):
    pass
    # start gunicorn
    # link nginx conf file to sites-enabled
    # sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
    # restart nginx
    # c.run(systemctl restart nginx)

@task
def stop(c):
    pass
    # stop gunicorn
    # unlink nginx conf file to sites-enabled
    # sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
    # restart nginx
    # c.run(systemctl restart nginx)

@task
def db_init(c):
    c.run('source /var/www/{0}/{0}_env/bin/activate'.format(APP_NAME))
    c.run('python -c "from {} import db, db.create_all()"'.format(APP_NAME))
    # c.run('chown root:indicator /var/www/{0}/{0}.db'.format(APP_NAME))

@task
def db_kill(c):
    pass

@task
def push_db(c):
    pass

@task
def pull_db(c):
    pass




