famille
=======

[![Build Status](https://travis-ci.org/m-vdb/famille.png)](https://travis-ci.org/m-vdb/famille)

A Django-based website.


Quick start
===========

Machine Dependencies
--------------------

- Install NodeJS v0.10.26: `brew install node`.
- Install virtualenv: `pip install virtualenv` or `easy_install virtualenv`.
- Install postgresql: `brew install postgresql`. You might encounter some issues with the installation of PostgreSQL, make sure your read every information from brew.
- Install foreman package: http://github.com/ddollar/foreman.

App installation
----------------

- Execute `make install`.
- Edit .env file (secret keys, database config).
- Start postgres server.
- Create a famille database in Postgres: `psql -h localhost -d postgres` and `create database famille;`.
- Load application fixtures: `make fixtures`.

Up and running
--------------

- Setup the database: `foreman run ./manage.py syncdb` and `foreman run ./manage.py migrate`.
- Execute `foreman run ./manage.py runserver` and access to http://localhost:8000.

Updating your environment
-------------------------

Whenever changes are pulled from remote repository, both database schema and dependencies might be
updated. You just have to run `make up` to be up to date.


Static pages (Flat pages)
-------------------------

Static pages are a good way to make content editable by user.
Some pages are required in the website. To load them (and maybe edit them),
you can perform `foreman run ./manage.py loaddata flatpages.json`

Once you edited the flatpages in the django admin, and you want to commit
your changes so that every app (heroku app for instance) has the changes,
you can execute `foreman run ./manage.py dumpdata flatpages --indent=4 > fixtures/flatpages.json`
before commiting your changes to git.

Migrating SQL Tables
--------------------

This project uses South. When you modify a model class (adding / removing / modifying column),
you just need to execute `make schemamigration` to migrate the database schema. And then
you need to apply it to the database by doing `make migrate`. While deploying on servers,
you only need to migrate since the schemamigration files are already there, because they are
versionned.
