from fabric import task

import os
import getpass

# create a new droplet if needed (-N)

APP_NAME = 'indicator'

USER = 'aganders3'
PUB_KEY = '~/.ssh/id_rsa.pub'

NGINX_USER = 'www-data'
NGINX_USER_GROUP = 'www-data'

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

    # create app virtual environment
    c.run('virtualenv /var/www/{0}/{0}_env'.format(APP_NAME))

    # create a directory for the gunicorn socket(s)
    c.run('mkdir /run/gunicorn')
    c.run('chown root:www-data /run/gunicorn')
    c.run('chmod 770 /run/gunicorn')
    c.run('chmod g+s /run/gunicorn')

    # set up UFW to allow nginx
    # set up SSH with Let's Encrypt

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
def update(c):
    c.local('git push live')

    with c.cd('/var/www/{0}'.format(APP_NAME)):
        # update venv
        c.run('./{}_env/bin/pip install -r requirements.txt'.format(APP_NAME))

        # link indicator.nginx to sites-available
        c.run('rm -f /etc/nginx/sites-enabled/{}'.format(APP_NAME))
        c.run('rm -f /etc/nginx/sites-available/{}'.format(APP_NAME))
        c.run('ln -s /var/www/{0}/{0}.nginx /etc/nginx/sites-available/{0}'.format(APP_NAME))

        # enable systemd service
        c.run('systemctl disable {}'.format(APP_NAME))
        c.run('systemctl enable /var/www/{0}/{0}.service'.format(APP_NAME))

    # add any cron job(s)

@task
def start(c):
    # start gunicorn
    c.run('systemctl start indicator')
    # link nginx conf file to sites-enabled
    c.run('ln -s /etc/nginx/sites-available/{0} /etc/nginx/sites-enabled/{0}'.format(APP_NAME))
    # restart nginx
    c.run('systemctl restart nginx')

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
    # TODO: set SQLAlchemy environment variable
    # check if DB already exists, request db_kill if you really want to
    # overwrite it
    with c.cd('/var/www/{0}'.format(APP_NAME)):
        c.run('source {0}_env/bin/activate; python -c "from {0} import db\ndb.create_all()"'.format(APP_NAME))

@task
def db_kill(c):
    # erase the old db (ask for confirmation)
    pass

@task
def push_db(c):
    pass

@task
def pull_db(c):
    pass

