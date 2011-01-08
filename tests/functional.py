import os
import shutil
import sys
import time

import tt

TESTDIR = "/tmp/ttfunctest"

def create():
    tt.TaskManager.TT_DIR = TESTDIR
    manager = tt.TaskManager()
    manager.initialize_state()


    task = manager.add_task(name="Develop tt sooner rather than later")
    manager.start_task(task)
    time.sleep(1)
    manager.stop_task(task)
    manager.start_task(task)
    time.sleep(2)
    manager.stop_task(task)

    print task.get_total_duration()
    print "created"

def destroy():
    shutil.rmtree(TESTDIR)
    print "destroyed"

def usage():
    cmd = "functional.py"
    print "%s <create|destroy>" % cmd
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    action = sys.argv[1]
    if action == "create":
        create()
    elif action == "destroy":
        destroy()
    else:
        print "unknown action"
        sys.exit(1)

