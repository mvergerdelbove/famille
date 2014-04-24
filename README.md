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
- Load application fixtures: `./manage.py loaddata prestataires.json`.
