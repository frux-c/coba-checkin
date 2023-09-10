# This is a full rundown of how to deploy a Django app on Ubuntu Server 22.04

### Current Ubuntu Version
`bash
lsb_release -a`

```bash
Distributor ID: Ubuntu
Description:    Ubuntu 22.04.3 LTS
Release:        22.04
Codename:       jammy
```

## Setting up the server
### Install Python 3.10
```bash
sudo apt update
sudo apt install python3.10
```

### Install Pip
```bash
sudo apt install python3-pip
```

### Install Virtualenv
```bash
sudo apt install python3-virtualenv
```

### Create a Virtual Environment
```bash
python3 -m venv <name of virtual environment>
```

### Install Apache2
```bash
sudo apt install apache2
```

### Install mod_wsgi
```bash
sudo apt install libapache2-mod-wsgi-py3
```

### Install Git (optional)
- This is only necessary if you want to clone your project from GitHub
    ```bash
    sudo apt install git
    ```
### Make sure that everything is up to date
```bash
sudo apt update
sudo apt upgrade
```
## Setting up the project
### Clone the project from GitHub (optional)
```bash
git clone <project url>
```
### Activate the virtual environment
```bash
source <name of virtual environment>/bin/activate
```

### Install project dependencies
```bash
pip install -r requirements.txt
```
### Collect static files
```bash
python manage.py collectstatic
```
### Migrate the database
```bash
python manage.py makemigrations
python manage.py migrate
```
### Create a superuser (optional)
```bash
python manage.py createsuperuser
```
### Allow the server's IP address to access the project
- This is only necessary if you want to access the project from the server's `IP address`
- Open the project's `settings.py` file
    ```bash
    nano <path to project>/settings.py
    ```
- Add the server's `IP address` to the `ALLOWED_HOSTS` list
    ```python
    ALLOWED_HOSTS = [
        'localhost',
        '<server IP address>',
    ]
    ```
- Save the file and exit
- We will later need to add the domain name to the `ALLOWED_HOSTS` list if we want to access the project from the domain name

## Setting up apache2 and mod_wsgi

### Create a new apache2 config file
-  First, lets check that apache2 is running properly
    ```bash
    sudo systemctl status apache2
    ```
-  If apache2 is running properly, we should see something like this:
    ```bash
    ● apache2.service - The Apache HTTP Server
        Loaded: loaded (/lib/systemd/system/apache2.service; enabled; vendor preset: enabled)
        Active: active (running) since Tue 2021-11-02 16:00:00 UTC; 1h 30min ago
        Docs: https://httpd.apache.org/docs/2.4/
        Main PID: 1234 (apache2)
        Tasks: 55 (limit: 2299)
        Memory: 6.1M
        CGroup: /system.slice/apache2.service
                ├─1234 /usr/sbin/apache2 -k start
                ├─1235 /usr/sbin/apache2 -k start
                └─1236 /usr/sbin/apache2 -k start
    ```
-  And also be able to see the default apache2 page at the server's `IP address`
-  With all that out of the way, we can start setting up the config file
-  We can start the config file by copying the default config file
    ```bash
    sudo cp /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/<name of config file>.conf
    ```
- Open the config file
    ```bash
    sudo nano /etc/apache2/sites-available/<name of config file>.conf
    ```
- Currently, the config file should look like this (with the exception of the comments):
    ```bash
    <VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>
    ```

- We need to add the following lines to the config file:
    ```conf
    Alias /static /path/to/static/files
    ```
- The `Alias` line tells apache2 where to find the static files for the project
- Next, we need to add the following lines to the config file:
    ```conf
    <Directory /path/to/static/files>
        Require all granted
    </Directory>
    ```
- The `Directory` line tells apache2 to allow access to the static files
- Next, we need to add the following lines to the config file:
    ```conf
    <Directory /path/to/project>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    ```
- The `Directory` line tells apache2 to allow access to the project files
- The `Files` line tells apache2 to allow access to the `wsgi.py` file
- Next, we need to add the following lines to the config file:
    ```conf
    WSGIDaemonProcess <name of project> python-path=/path/to/project python-home=/path/to/virtual/environment
    WSGIProcessGroup <name of project>
    WSGIScriptAlias / /path/to/project/wsgi.py
    ```
- The `WSGIDaemonProcess` line tells apache2 to create a daemon process for the project
- The `WSGIProcessGroup` line tells apache2 to use the daemon process for the project
- The `WSGIScriptAlias` line tells apache2 where to find the `wsgi.py` file
- This is recommended by the official Django documentation [here](https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/modwsgi/#using-mod-wsgi-daemon-mode)
- `Optionally`, if serving media files, we need to add the following lines to the config file:
    ```conf
    Alias /media /path/to/media/files
    <Directory /path/to/media/files>
        Require all granted
    </Directory>
    ```
- Same as the `Alias` and `Directory` lines for the static files
### Setting permissions for the apapche2 on the project files
- We need to set the permissions for the project so that apache2 can access the project files
- First, we need to add the apache2 user to the group that owns the project files
    ```bash
    sudo usermod -a -G <group that owns the project files> www-data
    ```
- Next, we need to change the permissions of the project files
    ```bash
    sudo chown -R <user that owns the project files>:<group that owns the project files> /path/to/project
    ```
- Next, we need to change the permissions of the virtual environment
    ```bash
    sudo chown -R <user that owns the project files>:<group that owns the project files> /path/to/virtual/environment
    ```
- Next, we need to change the permissions of the static files
    ```bash
    sudo chown -R <user that owns the project files>:<group that owns the project files> /path/to/static/files
    ```
- `Optionally`, if serving media files, we need to change the permissions of the media files
    ```bash
    sudo chown -R <user that owns the project files>:<group that owns the project files> /path/to/media/files
    ```
- The user or group should at least have read permissions for the project files and virtual environment
- The user or group should at least have read and execute permissions for the static files
- `Optionally`, if serving media files, the user or group should at least have read and execute permissions for the media files
- To check the permissions of the project files and virtual environment, run the following command:
    ```bash
    ls -l /path/to/project
    ls -l /path/to/virtual/environment
    ```
- Apache2 should now be able to access the project files (apache2 runs as the `www-data` user)
- Use the command below to change the permissions of the project files and virtual environment if apache2 is still unable to access the project files
    ```bash
    sudo chmod -R <permissions> /path/to/project
    sudo chmod -R <permissions> /path/to/virtual/environment
    ```
- If you are using the local sqlite3 database, you need to change the permissions of the database file
    ```bash
    sudo chmod -R <permissions> /path/to/database/file/sqlite3.db
    ```

## Enable the config file
- We need to enable the config file so that apache2 can use it
- First, we need to disable the default config file
    ```bash
    sudo a2dissite 000-default.conf
    ```
- Next, we need to enable the config file
    ```bash
    sudo a2ensite <name of config file>.conf
    ```
- Next, we need to restart apache2
    ```bash
    sudo systemctl restart apache2
    ```
- Apache2 should now be able to serve the project on the server's `IP address` `http://<IP address>`
- If apache2 is unable to serve the project, check the apache2 error log
    ```bash
    sudo tail -f /var/log/apache2/error.log
    ```
## Setting up the domain name
- We need to set up the domain name so that we can access the project from the domain name
- First, we need to accuire a domain name. This can be done from a domain name registrar like [Namecheap](https://www.namecheap.com/), [GoDaddy](https://www.godaddy.com/), or [Google Domains](https://domains.google/) (there are many more)
- Next, we need to point the domain name to the server's `IP address`

### Pointing the domain name to an internal IP address

- ### This is what I did for my project
    > - If the server is on the same network, we can point the domain using CNAMES
    > - **IMPORTANT** CNAMES are aliases for domain names, which means that our network has to be able to resolve the domain name to the server's `IP address` or else it will **NOT** work
    > - First, we need to create a CNAME record for the domain name
    > - Next, we need to point the CNAME record to the servers `internal domain name (hostname)`
    > - Next allow the external domain name to access the project
    > - Open the project's `settings.py` file
    >     ```bash
    >     nano <path to project>/settings.py
    >     ```
    > - Add the domain name to the `ALLOWED_HOSTS` list
    >     ```python
    >     ALLOWED_HOSTS = [
    >         'localhost',
    >         '<server IP address>',
    >         '<domain name>',
    >     ]
    >     ```
    > - Save the file and exit
    > - We should now be able to access the project from the domain name `http://<domain name>`
- If you are unable to access the project from the domain name, check the apache2 error log
- If you dont have a way to resolve the internal domain name, you can add it to your machines `hosts` file for `linux and mac`
    ```bash
    sudo nano /etc/hosts
    ```
- For `windows`, you can add it to the `hosts` file located at `C:\Windows\System32\drivers\etc\hosts`

    
    

## Some useful roadblocks and solutions
### If apache seems to constantly be loading the page
- I had this issue when I was setting up the project where apache2 would just constantly load the page. And after first load it would not even load on second refresh
- I found out that the wsgi application group was not setting up properly
- I fixed this by adding/changing the `WSGIProcessGroup` line in the config file to:
    ```conf
    WSGIApplicationGroup %{GLOBAL}
    ```