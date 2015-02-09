""" (Compute) Unit tests
"""
import os
import sys
import radical.pilot
import unittest

import uuid
from copy import deepcopy
from radical.pilot.db import Session
from pymongo import MongoClient

# RADICAL_PILOT_DBURL defines the MongoDB server URL and has the format
# mongodb://host:port/db_name

RP_DBENV = os.environ.get("RADICAL_PILOT_DBURL")
if not RP_DBENV:
    print "ERROR: RADICAL_PILOT_DBURL (MongoDB server URL) is not defined."
    sys.exit(1)

RP_DBURL = ru.Url (RP_DBENV)
if not (RP_DBURL.path and len(RP_DBURL.path) > 1):
    RP_DBURL=ru.generate_id ('rp_test.')

DBURL      = ru.URL(RP_DBURL)
DBURL.path = None
DBURL      = str(DBURL)

DBNAME     = RP_DBURL.path.lstrip('/')


#-----------------------------------------------------------------------------
#
class TestIssue213(unittest.TestCase):
    # silence deprecation warnings under py3

    def setUp(self):
        # clean up fragments from previous tests
        client = MongoClient(DBURL)
        client.drop_database(DBNAME)

        self.test_resource = os.getenv('RADICAL_PILOT_TEST_REMOTE_RESOURCE',     "local.localhost")
        self.test_ssh_uid  = os.getenv('RADICAL_PILOT_TEST_REMOTE_SSH_USER_ID',  None)
        self.test_ssh_key  = os.getenv('RADICAL_PILOT_TEST_REMOTE_SSH_USER_KEY', None)
        self.test_workdir  = os.getenv('RADICAL_PILOT_TEST_REMOTE_WORKDIR',      "/tmp/radical.pilot.sandbox.unittests")
        self.test_cores    = os.getenv('RADICAL_PILOT_TEST_REMOTE_CORES',        "1")
        self.test_timeout  = os.getenv('RADICAL_PILOT_TEST_TIMEOUT',             "2")
        self.test_runtime  = os.getenv('RADICAL_PILOT_TEST_RUNTIME',             "1")

    def tearDown(self):
        # clean up after ourselves 
        client = MongoClient(DBURL)
        client.drop_database(DBNAME)

    def failUnless(self, expr):
        # St00pid speling.
        return self.assertTrue(expr)

    def failIf(self, expr):
        # St00pid speling.
        return self.assertFalse(expr)

    #-------------------------------------------------------------------------
    #
    def test__issue_213(self):
        """ Test if we can wait for different pilot states.
        """
        session = radical.pilot.Session(database_url=DBURL)
        c = radical.pilot.Context('ssh')
        c.user_id  = self.test_ssh_uid
        c.user_key = self.test_ssh_key

        session.add_context(c)

        pm = radical.pilot.PilotManager(session=session)

        cpd = radical.pilot.ComputePilotDescription()
        cpd.resource          = self.test_resource
        cpd.cores             = self.test_cores
        cpd.runtime           = self.test_runtime
        cpd.sandbox           = self.test_workdir

        pilot = pm.submit_pilots(pilot_descriptions=cpd)

        assert pilot is not None

        pilot.wait(state=radical.pilot.ACTIVE, timeout=self.test_timeout*60)
        assert pilot.state == radical.pilot.ACTIVE

        # the pilot should finish after it has reached run_time
        pilot.wait(timeout=self.test_timeout*60)
        assert pilot.state == radical.pilot.DONE

        session.close()

