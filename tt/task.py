import datetime
import errno
import os

from tt import exceptions
from tt import utils


class Task(object):

    DIRECTORY_STATUSES = ("pending", "started", "stopped", "done")
    UNLINKED_STATUSES = ("closed", "deleted")
    STATUSES = DIRECTORY_STATUSES + UNLINKED_STATUSES
    
    def __init__(self, manager, task_id, name, status, log=None):
        self.manager = manager
        self.task_id = task_id
        self.name = name
        self.status = status
        self.log = log or []

    @classmethod
    def create(cls, manager, name, status):
        task_id = cls._generate_task_id(name)
        task = cls(manager=manager, task_id=task_id, name=name, status=status)
        return task

    @classmethod
    def load(cls, manager, task_id):
        task_file = cls._get_task_file(manager, task_id)
        if not os.path.exists(task_file):
            raise exceptions.BadTaskId("'%s' does not exist" % task_id)

        task = cls.load_from_file(manager, task_file)
        return task

    @classmethod
    def load_from_file(cls, manager, task_file):
        with open(task_file, "r") as f:
            lines = f.readlines()

            name = lines[0].rstrip('\n')

            # The last status line reflects the current status
            status_line = lines[-1].rstrip('\n')
            status, _ = status_line.split(" ", 1)

            # Parse the timecard
            log = []
            status_lines = lines[1:]
            for status_line in status_lines:
                status, timestamp = status_line.rstrip('\n').split(" ", 1)
                dt = utils.get_datetime_from_str(timestamp)
                log.append((status, dt))

            task_id = cls._get_task_id_from_task_file(task_file)
            task = cls(manager=manager, task_id=task_id, name=name, status=status,
                       log=log)
            return task

    @classmethod
    def _generate_task_id(cls, name):
        """Generate a task_id string comprising a slugified form of the task
        name and the date the task was created.

        Assuming that no two tasks slugify to the same thing on a given date.
        May have to change this assumption later.
        """
        slug = cls._slugify(name)
        now = utils.get_now()
        date_str = utils.format_date_str(now, fmt="%Y_%m_%d")
        task_id = "%s-%s" % (slug, date_str)
        return task_id

    @classmethod
    def _get_task_id_parts(cls, task_id):
        """Return the components of a task_id"""
        try:
            slug, date_str = task_id.split("-")
            year, month, day = date_str.split("_")
            return (slug, year, month, day)
        except ValueError:
            raise exceptions.BadTaskId("'%s' is not a valid task_id" % task_id)

    @classmethod
    def _slugify(cls, name, max_len=16):
        INVALID_CHARS = ["/", ":", "-", '"', "'"]
        slug = name.replace(" ", "_")

        for char in INVALID_CHARS:
            slug = slug.replace(char, "_")
        
        slug = slug.lower()
        return slug[:max_len]

    def __repr__(self):
        return "<Task task_id='%s' status='%s'>" % (self.task_id, self.status)

    @classmethod
    def _get_task_dir(cls, manager, task_id):
        tasks_dir = manager._get_tasks_dir()
        slug, year, month, day = cls._get_task_id_parts(task_id)
        task_dir = os.path.join(tasks_dir, year, month, day)
        return task_dir

    def get_task_file(self):
        task_file = self._get_task_file(self.manager, self.task_id)
        return task_file

    @classmethod
    def _get_task_file(cls, manager, task_id):
        """Return the file under tasks/year/month/day/slug for this task"""
        task_dir = cls._get_task_dir(manager, task_id)
        slug, year, month, day = cls._get_task_id_parts(task_id)
        task_file = os.path.join(task_dir, slug)
        return task_file

    @classmethod
    def _get_task_id_from_task_file(cls, task_file):
        """Return the task_id for a given task_file

        ./tasks/2011/1/2/do_something -> do_something-2011-01-02
        """
        base, slug = os.path.split(task_file)
        base, day = os.path.split(base)
        base, month = os.path.split(base)
        base, year = os.path.split(base)
        date_str = "%s_%s_%s" % (year, month, day)
        return "%s-%s" % (slug, date_str)

    def _append_task_file(self, line):
        task_file = self._get_task_file(self.manager, self.task_id)
        with open(task_file, "a") as f:
            f.write("%s\n" % line)

    def _append_status_timestamp(self):
        now = utils.get_now()
        datetime_str = utils.format_datetime_str(now)
        timelog = "%s %s" % (self.status, datetime_str)
        self._append_task_file(timelog)
        self.log.append((self.status, now))

    def initialize_task(self):
        """Create the task in its inital state under the task/ dir"""
        task_dir = self._get_task_dir(self.manager, self.task_id)
        utils.mkdirs_easy(task_dir)

        task_file = self._get_task_file(self.manager, self.task_id)

        if os.path.exists(task_file):
            raise exceptions.TaskAlreadyExists(
                "'%s' already exists" % self.task_id)

        with open(task_file, "w") as f:
            f.write("%s\n" % self.name)

        self._initialize_task_status()

    def _initialize_task_status(self):
        """Add this task to the state/status/ table"""
        task_file = self._get_task_status_file()
        try:
            with open(task_file, "w") as f:
                f.write("")  # The files presence is all that matters
        except IOError, e:
            if e.errno == errno.ENOENT:
                task_path = os.path.dirname(task_file)
                raise exceptions.DirectoryNotFound(
                    "'%s' not found" % task_path)
            else:
                raise

        self._append_status_timestamp()

    def _get_task_status_file(self):
        status_dir = self.manager._get_status_dir(self.status)
        task_file = os.path.join(status_dir, self.task_id)
        return task_file

    def _move_status_link(self, status):
        """Update state/status table and write timelog"""
        if status == self.status:
            raise exceptions.StatusChangeException(
                "New status must be different than %s" % self.status)

        old_task_file = self._get_task_status_file()
        self.status = status
        new_task_file = self._get_task_status_file()
        os.rename(old_task_file, new_task_file)
        self._append_status_timestamp()

    def _remove_status_link(self):
        task_status_file = self._get_task_status_file()
        os.unlink(task_status_file)

    def _remove_task_file(self):
        task_file = self.get_task_file()
        os.unlink(task_file)

    def start(self):
        if self.status not in ("pending", "stopped"):
            raise exceptions.StatusChangeException("Task must be pending or stopped")

        self._move_status_link("started")

    def stop(self):
        if self.status != "started":
            raise exceptions.StatusChangeException("Task must be started")

        self._move_status_link("stopped")
    
    def done(self):
        if self.status != "stopped":
            raise exceptions.StatusChangeException("Task must be stopped")

        self._move_status_link("done")

    def close(self):
        if self.status != "done":
            raise exceptions.StatusChangeException("Task must be done")

        self._remove_status_link()
        self.status = "closed"
        self._append_status_timestamp()

    def delete(self):
        if self.status == "closed":
            raise exceptions.StatusChangeException("Task cannot be closed")

        self._remove_status_link()
        self._remove_task_file()

    def get_duration(self):
        """
        For an unbounded interval, the duration is "running", so the imposed
        boundary is now.
        """
        boundary = utils.get_now()
        return self._get_duration(self.log, boundary)

    def _get_duration(self, entries, boundary):
        """Return the task duration as a `datetime.timedelta` object.

        The duration of a task is defined as the sum of its started-stopped
        intervals.

        Intervals fall into 3 categories:

        1. A 'bounded interval' is where a 'started' status has a matching
           'stopped' status. The duration of the interval is
           (stop_time - start_time).

        2. An 'unbounded interval' has 2 possibilities:

            a. Where the 'started' status is the last entry in the log. In
               this case, the duration of the interval is (now - start_time)

            b. Where the 'stopped' status is the first entry in the log for
               that date. In this case, the duration of the interval is
               (stopped_time - midnight)

        3. An 'invalid interval' is one where the 'started' status does not
           have a matching 'stopped' status *and* 'started' is not the last
           entry. This is a state violation and raises a
           StatusChangeException.
        """
        intervals = []
        started = None
        for status, dt in entries:
            if status == "started" and not started:
                started = dt
            elif started and status == "stopped":
                # 1. bounded interval
                stopped = dt
                timedelta = stopped - started
                # NOTE: oddly timedelta doesn't support the += operator in
                # (2.6)
                intervals.append(timedelta)
                started = None
            elif not started and status == "stopped":
                # 2b. unbounded interval - unclosed stop
                stopped = dt
                midnight = utils.date2datetime(stopped.date())
                timedelta = stopped - midnight
                intervals.append(timedelta)
            elif started:
                # 3. invalid interval
                raise exceptions.StatusChangeException(
                    "'started' entry must have matching 'stopped' entry or be "
                    "the last entry in the log")

        if started:
            # 2a. unbounded interval - unclosed start
            timedelta = boundary - started
            intervals.append(timedelta)

        total = sum(intervals, datetime.timedelta())
        return total

    def get_log_entries_for_date(self, date):
        for entry in self.log:
            status, dt = entry
            if utils.date_match(date, dt):
                yield entry

    def get_duration_for_date(self, date):
        """Return the task duration for a given date.

        1. If we're asked for today, we should calculate the time up to this
           moment (now).

        2. If we're asked for a date in the past, we should use midnight as
           the boundary.
        """
        entries = self.get_log_entries_for_date(date)
        now = utils.get_now()
        today = utils.date_match(now, date)

        if today:
            # 1. today
            boundary = now
        else:
            # 2. past
            dt = utils.date2datetime(date)
            midnight = dt + datetime.timedelta(days=1)
            boundary = midnight

        duration = self._get_duration(entries, boundary)
        return duration

