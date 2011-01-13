============
Design Notes
============


The design is modeled on git, a database within the filesystem.


Task IDs
========

Whereas `git` uses SHA1s for object IDs, `tt` uses a more human-friendly
system: the task name (slugified and truncated) and the task creation date.

Since `tt` provides tab-completion on task_ids, you rarely have to type out
the entire ID. Rather, you type in the first two-letters of the task name
(lowercased) then press TAB, the rest of the id should fill in automatically.


Task File
=========

Each task in the system is represented by a single file. The first line is the
pretty description. The remaining lines are the timestamps of the status
changes. These are used by the reporting system to tabulate task duration.

Since this is just a plain text file, you are free to edit this as needed. The
only caveat is: ensure the state changes make-sense (e.g. don't start a closed
task, etc.)


Task Status
===========

A task is given a particular status by placing a pointer-file in the
`state/status` directory. The pointer-file is empty, its name, which is the
task_id, is the only part that is needed.

This could be a symlink (?).


Task Manager
============

This is the component that manages multiple tasks, like fetching tasks with a
given status, or tasks that were started on a particular date.


Filesystem Layout
=================

Layout::
    .tt/
      state/
        status/
          pending/
            design_session-2011_1_08
          started/
          stopped/
          done/
      tasks/
        2011/
          01/
            08/
              design_session
                Design Session
                pending <timestamp>
                started <timestamp>
                stopped <timestamp>
                done <timestamp>
                closed <timestamp>
