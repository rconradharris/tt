===========================
tt - the stupid timetracker
===========================


Introduction
============

`tt` is a command-line time-tracker that:

    * Stores everything as regular files which can be edited as needed
    * Uses bash completion to make task switching quick and painless
    * Provides simple reports to see where your time was spent

As a bonus, since everything is stored in plain text-files, `tt` plays well
with `git`, meaning you can get backup (via `git push remote`) and
change-tracking (via `git diff`) for free.


Installation
============

Run::

    $ python setup.py build
    $ python setup.py install

Add the following line to your .bashrc or .profile::

    . /etc/tt_bash_completion_hook


Usage
=====

Initialize the tt repo::

    $ tt init

Add a task::

    $ tt add Create README file

Show current status::

    $ tt ls
    STARTED

    STOPPED

    PENDING

     - Create README file

    DONE

    Total Duration: 00:00:00

Start a task::

    $ tt start cr[TAB-complete]eate_readme_fi-2011_01_09

Stop the current task::

    $ tt stop

Finish a task::

    $ tt done cr[TAB-complete]eate_readme_fi-2011_01_09

    $ tt ls
    STARTED

    STOPPED

    PENDING

    DONE

     - Create README file (00:00:13)

    Total Duration: 00:00:13

Close finished tasks::

    $ tt close

    $ tt ls
    STARTED

    STOPPED

    PENDING

    DONE

    Total Duration: 00:00:00

Delete a task::

    $ tt rm cr[TAB-complete]eate_readme_fi-2011_01_09

Report for today::

    $ tt report today
    2011-01-11
     - Create the Report Component (01:30:00)
     - Add some Tests for Duration (00:45:00)

    Total Duration: 02:15:00

Report for week::

    $ tt report week
    2011-01-11: 02:15:00
    2011-01-10: 00:45:00
    2011-01-09: 00:00:00
    2011-01-08: 00:00:00
    2011-01-07: 00:00:00
    2011-01-06: 00:00:00
    2011-01-05: 00:00:00

Bulk load tasks::

    $ tt add < daily.txt
