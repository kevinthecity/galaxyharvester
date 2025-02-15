# Galaxy Harvester Web Application

## Initial Setup

### Galaxy Harvester Server Requirements:
The following software must be set up on the server prior to setting up Galaxy Harvester (The versions listed reflect what the current code base is running on)

* Webserver (apache2 2.4)
* MySQL/MariaDB Server (5.8)
* Python (3.6)
 * module: pymysql (0.10)
 * module: jinja2 (2.11)
 * module: Pillow (8.0)

### Web Server Configuration:
The web server being used must be configured to serve the Python based CGI scripts as follows

* Set "html" folder of this repo as web site root (for apache2 update DocumentRoot in /etc/apache2/sites-enabled/000-default.conf)
* Enable CGI in your webserver, for apache2 you can run "sudo a2enmod cgi" and add the line "AddHandler cgi-script .py" in /etc/apache2/conf-enabled/serve-cgi-bin.conf within the Directory block which should be updated to point to your html folder.
* The folders should be writable by the web server: html/temp, html/images/users, html/images/schematics


### Database Creation:
The database folder contains scripts and seed data to initialize a ready to use Galaxy Harvester database.

1. Verify database/createSWGresourcedb.sql LOAD DATA commands reflect the absolute path of the seedData files
2. Change grant statements in database/createSWGresourcedb.sql to target your db user or create new default user in mysql: "CREATE USER 'webusr'@'localhost' IDENTIFIED BY '';"
2. run "mysql -u root -p --local-infile < createSWGresourcedb.sql" to create the database

### Site Configuration:
The site configuration files should exist in the folder above the web site root folder along with the maintenance job scripts, update the following 3 files with appropriate passwords, etc.

* Update env.py so host, user, and password reflect your mysql server info if not using default webuser
* Update env.py so outgoing mail server and login info is set properly


### Site Maintenance Jobs (Cron, etc):
These jobs should be set up to run at regular intervals to maintain the site and provide features.

* resourceDump.py Daily (provides csv and xml format exports of current resources for each galaxy)
* cleanupDaily.py Daily (performs automated cleanup of old site data)
* checkAlerts.py Every 30 minutes (checks recent resource activity for user alert triggers and sends those alerts)
* catchupMail.py Hourly (checks for pending email alerts that have been stalled due to email failure and retrys them)

## Development

### Tools
You'll want to have these additional tools available locally to build and test Galaxy Harvester

* python-nose
* python-nose-cov

With those installed, you should be able to run nose2 from the test/pyunit folder to validate the code with a unit test run.

### Seed Data Refresh
Galaxy Harvester seed data includes creature and schematic data that is automatically generated from the SWGEmu source code repository.  The "scripts" folder contains utility scripts to extract this data from the SWGEmu code in the event that it needs to be regenerated after changes.  These scripts operate on a local database, so the process of refresh would look something like these steps:

1. Delete all data from the relevant tables in the local database
2. Check out the SWGEmu Core3 git repository to the location referenced in utility script
3. Execute the utility script (Depending on the state of the code you may need to delete or change some files and go back to step 1.  Sometimes there are invalid or duplicate lua files in the repository that cause problems.)
4. Export the data from all relevant tables to the database/seedData folder overwriting the old seed data files.  Those can now be imported to other environments with one of the scripts in database/updateRefresh.

### Presentation Templates
In most cases, Galaxy Harvester uses the [Jinja2](http://jinja.pocoo.org/) template engine to render any html to the user.  The html folder contains various scripts, some of which are called by AJAX from an already rendered page, and some of which render one of the templates under html/templates.  The blocks.html template is not rendered directly but has various blocks like headers and footers that are imported by the other templates.

## Local Development on M2 Mac

### Commands
brew services start mysql
brew services restart mysql
tail -f /opt/homebrew/var/log/httpd/error_log

cd /opt/homebrew/var/www

#### Install mysql via homebrew
brew install mysql

### optional? 
mysql_secure_installation

### Create user
mysql -u root -p

CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'newuser'@'localhost' WITH GRANT OPTION;

### Allow local data writing to mysql
Add `local_infile=1` to /opt/homebrew/etc/my.cnf

```
# Default Homebrew MySQL server config
[mysqld]
local_infile=1 <<<
# Only allow connections from localhost
bind-address = 127.0.0.1
mysqlx-bind-address = 127.0.0.1
```

### Load the DB
mysql -u root -p --local-infile < database/createSWGresourcedb.sql

## Install Apache

brew install httpd

### Edit httpd.conf

Consider making a copy of this for easy reverting
/opt/homebrew/etc/httpd/httpd.conf

Uncomment `LoadModule cgi_module lib/httpd/modules/mod_cgi.so`

<IfModule mpm_prefork_module>
	LoadModule cgi_module lib/httpd/modules/mod_cgi.so
</IfModule>

Add html to doc root and directory below it
`DocumentRoot "/opt/homebrew/var/www"` -> `DocumentRoot "/opt/homebrew/var/www/html"`
`<Directory "/opt/homebrew/var/www">` -> `<Directory "/opt/homebrew/var/www/html">`

Change 
<Directory "/opt/homebrew/var/www/cgi-bin">
    AllowOverride None
    Options None
    Require all granted
</Directory>

to

<Directory "/opt/homebrew/var/www/html">
    AllowOverride None
    Options ExecCGI
    Require all granted
</Directory>

Find
`AddHandler cgi-script .cgi`

and change to

`AddHandler cgi-script .cgi .py`

## Clone repo

- Navigate to /opt/homebrew/var/www
- Clone this repo in the folder
- Rename www to www.original
- Rename newly cloned project to www

## Maybe it all works now?

## How to add logging

import logging

logging.basicConfig(filename='/opt/homebrew/var/log/myapp.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

e.g. logging.info(spawn.getJSON())
