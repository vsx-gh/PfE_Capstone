#!/usr/bin/env python

'''
Program:     pgaws.py
Author:      Jeff VanSickle
Created:     20170117
Modified:    20170117

Program creates connection to AWS RDS instance and returns cursor to the
instance and DB specified.

Most connection options kept in environment variables. Best practice would
be to encrypt these. That is a feature request for this code.

I keep a read-only user password in /etc/pgaws/aws_config and lock down
perms to that file. Once again, will move this to an encrypted string stored
in an environment variable soon.

UPDATES:
    yyyymmdd JV - Changed something, commenting here

INSTRUCTIONS:
    Use /etc/environment to define environment variables

TO DO:
    Set up PGP/GPG with Python to encrypt variables properly
'''

import psycopg2
import os

def create_cursor():
    pginst = os.getenv('PGINST', None).strip().replace('"', '')     # RDS instance
    pgport = os.getenv('PGPORT', None).strip().replace('"', '')     # Port
    pgdb = os.getenv('PGDB', None).strip().replace('"', '')         # Database in RDS
    pguser = os.getenv('PGUSER', None).strip().replace('"', '')     # Read-only!
    pgsslmode = os.getenv('PGSSLMODE', None).strip().replace('"', '')    # verify-full
    pgsslcert = '<AWS_RDS_CERT>'     # AWS gives you this cert
    pgpassloc = '<YOUR_AWS_CONFIG>'  # Password stored here

    with open(pgpassloc, 'r') as passfile:
        for item in passfile:
            pgpass = item.strip()

    conn_str = "host='{}' port='{}' dbname='{}' user='{}' password='{}' sslmode='{}' sslrootcert='{}'".format(pginst, pgport, pgdb, pguser, pgpass, pgsslmode, pgsslcert)

    conn = psycopg2.connect(conn_str)
    dbcursor = conn.cursor()

    return dbcursor
