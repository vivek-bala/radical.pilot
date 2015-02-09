import os
import sys
import radical.pilot as rp

# ATTENTION:
#
# This example needs significant time to run, and there is some probability that
# the larger futuregrid pilots are not getting through the batch queue at all.
# It is thus not part of the RP test suite.

# READ: The RADICAL-Pilot documentation: 
#   http://radicalpilot.readthedocs.org/en/latest
#
# Try running this example with RADICAL_PILOT_VERBOSE=debug set if 
# you want to see what happens behind the scences!


#------------------------------------------------------------------------------
#
def pilot_state_cb (pilot, state) :
    """ this callback is invoked on all pilot state changes """

    print "[Callback]: ComputePilot '%s' state: %s." % (pilot.uid, state)

    if  state == rp.FAILED :
        sys.exit (1)


#------------------------------------------------------------------------------
#
def unit_state_cb (unit, state) :
    """ this callback is invoked on all unit state changes """

    print "[Callback]: ComputeUnit  '%s' state: %s." % (unit.uid, state)

    if  state == rp.FAILED :
        sys.exit (1)


#------------------------------------------------------------------------------
#
if __name__ == "__main__":

    # Create a new session. A session is the 'root' object for all other
    # RADICAL-Pilot objects. It encapsualtes the MongoDB connection(s) as
    # well as security crendetials.
    session    = rp.Session()
    session_id = session.uid
    print "========================="
    print session_id
    print "========================="

    # Add a Pilot Manager. Pilot managers manage one or more ComputePilots.
    pmgr = rp.PilotManager(session=session)

    # Register our callback with the PilotManager. This callback will get
    # called every time any of the pilots managed by the PilotManager
    # change their state.
    pmgr.register_callback(pilot_state_cb)

    pdesc = rp.ComputePilotDescription()
    pdesc.resource  = "local.localhost"
    pdesc.runtime   = 12 # minutes
    pdesc.cores     = 4
    pdesc.cleanup   = True

    pilot_1 = pmgr.submit_pilots(pdesc)

    # create a second pilot with a new description
    pdesc = rp.ComputePilotDescription()
    pdesc.resource  = "xsede.stampede"
    pdesc.runtime   = 40 # minutes
    pdesc.cores     = 32
    pdesc.project   = "TG-MCB090174"

    pilot_2 = pmgr.submit_pilots(pdesc)

    # reuse the pilot description for the third pilot
    pdesc.cores     = 128

    pilot_3 = pmgr.submit_pilots(pdesc)

    # Combine the ComputePilot, the ComputeUnits and a scheduler via
    # a UnitManager object.
    umgr = rp.UnitManager (session=session, scheduler=rp.SCHED_BACKFILLING)

    # Register our callback with the UnitManager. This callback will get
    # called every time any of the units managed by the UnitManager
    # change their state.
    umgr.register_callback(unit_state_cb)

    # Add the previsouly created ComputePilot to the UnitManager.
    umgr.add_pilots([pilot_1, pilot_2, pilot_3])

  # # wait until first pilots become active
    pilot_1.wait (state=rp.ACTIVE)

    # Create a workload of 8 ComputeUnits.  
    cus = list()

    for unit_count in range(0, 512):
        cu = rp.ComputeUnitDescription()
        cu.kernel      = 'SLEEP'
        cu.arguments   = ["300"]
        cus.append(cu)

    # Submit the previously created ComputeUnit descriptions to the
    # PilotManager. This will trigger the selected scheduler to start
    # assigning ComputeUnits to the ComputePilots.
    units = umgr.submit_units(cus)

    # Wait for all compute units to reach a terminal state (DONE or FAILED).
    umgr.wait_units()

    pmgr.cancel_pilots ()

    for unit in units:
        print "* Unit %s state: %s, exit code: %s, started: %s, finished: %s" \
            % (unit.uid, unit.state, unit.exit_code, unit.started, unit.finished)

    # Close automatically cancels the pilot(s).
    print "========================="
    print session_id
    print "========================="
    session.close(cleanup=False)

    os.system ('radicalpilot-stats -m stat,plot -s %s' % session_id)

