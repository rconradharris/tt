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

    $ tt info
        STARTED

        STOPPED

        PENDING

         - Create README file

        DONE

        Total Duration: 0 seconds

Start a task::

    $ tt start cr[TAB-complete]eate_readme_fi-2011_01_09

Stop a task::

    $ tt stop cr[TAB-complete]eate_readme_fi-2011_01_09

Finish a task::

    $ tt done cr[TAB-complete]eate_readme_fi-2011_01_09

    $ tt info
        STARTED

        STOPPED

        PENDING

        DONE

         - Create README file (13 seconds)

        Total Duration: 13 seconds

Close finished tasks::

    $ tt close

    $ tt info
        STARTED

        STOPPED

        PENDING

        DONE

        Total Duration: 0 seconds

Report for today::

    $ tt report today
    2011-01-11

     - Create the Report Component (01:30:00)
     - Add some Tests for Duration (00:45:00)

     Total Duration: 02:15:00
