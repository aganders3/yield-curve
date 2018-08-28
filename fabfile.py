from fabric import task

import os
import getpass
import subprocess

# create a new droplet if needed (-N)

APP_NAME = 'indicator'
DOMAIN = 'market-weather.com'

USER = 'aganders3'
PUB_KEY = '~/.ssh/id_rsa.pub'
PUB_KEY_MD5 = '96:83:bc:22:5f:ad:92:97:cd:20:e8:2f:3d:51:8c:7c'

NGINX_USER = 'www-data'
NGINX_USER_GROUP = 'www-data'

@task
def create(c):
    create_droplet = ['doctl', 'compute', 'droplet', 'create']

    droplet_name = input("Enter a droplet name: ")
    create_droplet += [droplet_name]

    create_droplet += ['--size', 's-1vcpu-1gb']
    create_droplet += ['--image', 'ubuntu-18-04-x64']
    create_droplet += ['--region', 'nyc1']
    create_droplet += ['--ssh-keys', PUB_KEY_MD5]
    create_droplet += ['--region', 'nyc1']
    create_droplet += ['--wait']
    create_droplet += ['--format', 'ID,Name,PublicIPv4']
    create_droplet += ['--no-header']

    p = subprocess.run(create_droplet, stdout=subprocess.PIPE)
    droplet_info = p.stdout.decode('utf-8')
    print("Created a new droplet!")
    print("ID\tName\tIP")
    print(droplet_info)

@task
def destroy(c):
    prompt = "Enter the number of a droplet to destroy it: "
    droplet_to_destroy, droplets = select_droplet(prompt)

    if (droplet_to_destroy is None or
        droplet_to_destroy < 0 or
        droplet_to_destroy >= len(droplets)):
        print("Invalid droplet selected")
        return 1
    else:
        drop_id, drop_name, drop_ip = droplets[droplet_to_destroy].split()

    delete_droplet = ['doctl', 'compute', 'droplet', 'delete']
    delete_droplet += [str(drop_id)]

    p = subprocess.run(delete_droplet)

def select_droplet(prompt="Select a droplet: "):
    list_droplets = ['doctl', 'compute', 'droplet', 'list']
    list_droplets += ['--format', 'ID,Name,PublicIPv4']
    list_droplets += ['--no-header']
    p = subprocess.run(list_droplets, stdout=subprocess.PIPE)
    droplets = p.stdout.decode('utf-8').split('\n')[:-1]

    print("Index\t\tID\tName\tIP")
    for i, droplet in enumerate(droplets):
        print(i, ":\t", droplet)

    try:
        selected = int(input(prompt))
    except ValueError:
        selected = None
    finally:
        return selected, droplets

@task
def init(c):
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

    # create app virtual environment
    c.run('virtualenv /var/www/{0}/{0}_env'.format(APP_NAME))

    # create a directory for the gunicorn socket(s) and database(s)
    c.run('mkdir -p /run/gunicorn')
    c.run('chown root:{} /run/gunicorn'.format(NGINX_USER_GROUP))
    c.run('chmod 770 /run/gunicorn')
    c.run('chmod g+s /run/gunicorn')

    # set environment variables for config
    c.run(('echo "export DB_BASE_DIR=\\"/run/gunicorn\\"" '
           '>> /etc/profile.d/{}.sh').format(APP_NAME))

    # set up UFW to allow nginx and OpenSSH
    c.run('ufw allow OpenSSH')
    c.run('ufw allow "Nginx Full"')
    c.run('ufw enable')
    c.run('ufw status')

    # TODO: set up SSH with Let's Encrypt

    # set remote for local git with server name
    # TODO: set the remote name to be that of the droplet or otherwise
    # troubleshoot the occasion where live already exists
    c.local(('git remote add live '
             'ssh://{}@{}/var/repo/{}.git').format(c.user, c.host, APP_NAME))

    # push up the code
    c.local('git push --set-upstream live master')
    with c.cd('/var/www/{0}'.format(APP_NAME)):
        # update venv
        c.run('./{}_env/bin/pip install -r requirements.txt'.format(APP_NAME))

        # link indicator.nginx to sites-available
        c.run('rm -f /etc/nginx/sites-available/{}'.format(APP_NAME))
        c.run('ln -s /var/www/{0}/{0}.nginx /etc/nginx/sites-available/{0}'.format(APP_NAME))

        # enable systemd service
        c.run('systemctl enable /var/www/{0}/{0}.service'.format(APP_NAME))

    # initialize the database
    db_init(c)

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
def update(c, stop_server=True, start_server=True):
    if stop_server:
        stop(c)

    c.local('git push live')

    with c.cd('/var/www/{0}'.format(APP_NAME)):
        # update venv
        c.run('./{}_env/bin/pip install -r requirements.txt'.format(APP_NAME))

        # link indicator.nginx to sites-available
        c.run('rm -f /etc/nginx/sites-available/{}'.format(APP_NAME))
        c.run('ln -s /var/www/{0}/{0}.nginx /etc/nginx/sites-available/{0}'.format(APP_NAME))

        # enable systemd service
        c.run('systemctl disable {}'.format(APP_NAME))
        c.run('systemctl enable /var/www/{0}/{0}.service'.format(APP_NAME))

    # TODO: add any cron job(s)

    if start_server:
        start(c)

@task
def start(c):
    # start gunicorn
    c.run('systemctl start {}'.format(APP_NAME))
    # link nginx conf file to sites-enabled
    c.run('ln -s /etc/nginx/sites-available/{0} /etc/nginx/sites-enabled/{0}'.format(APP_NAME))
    # restart nginx
    c.run('systemctl restart nginx')

@task
def stop(c):
    # stop gunicorn
    c.run('systemctl stop {}'.format(APP_NAME))
    # unlink nginx conf file to sites-enabled
    c.run('rm -f /etc/nginx/sites-enabled/{}'.format(APP_NAME))
    # restart nginx
    c.run('systemctl restart nginx')

@task
def db_init(c):
    # check if DB already exists, request db_kill if you really want to
    # overwrite it
    with c.cd('/var/www/{}'.format(APP_NAME)), c.prefix('export DB_BASE_DIR="/run/gunicorn"'):
        c.run('source {0}_env/bin/activate; echo -e "from {0} import db\ndb.create_all()" | python'.format(APP_NAME))

@task
def db_kill(c):
    print("YOU ARE ABOUT TO DELETE THIS DATABASE FILE ON THE SERVER:")
    c.run('ls -l /run/gunicorn/{}.db'.format(APP_NAME))
    print("WARNING: THIS ACTION CANNOT BE UNDONE")
    kill = input("ARE YOU SURE? [y/N]: ")
    if kill == 'y':
        c.run('rm -f /run/gunicorn/{}.db'.format(APP_NAME))

@task
def push_db(c):
    c.put('{}.db'.format(APP_NAME),
          '/run/gunicorn')

@task
def pull_db(c):
    c.get('/run/gunicorn/{}.db'.format(APP_NAME))

