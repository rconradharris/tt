import errno
import os

from tt import exceptions
from tt import utils


class Task(object):

    DIRECTORY_STATUSES = ("pending", "started", "stopped", "done")
    UNLINKED_STATUSES = ("closed", "deleted")
    STATUSES = DIRECTORY_STATUSES + UNLINKED_STATUSES
    
    def __init__(self, manager, task_id, name, status):
        self.manager = manager
        self.task_id = task_id
        self.name = name
        self.status = status

    @classmethod
    def create(cls, manager, name, status):
        task_id = cls._generate_task_id(name)
        task = cls(manager=manager, task_id=task_id, name=name, status=status)
        return task

    @classmethod
    def load(cls, manager, task_id):
        name, status = cls._load_name_and_status(manager, task_id)
        task = cls(manager=manager, task_id=task_id, name=name, status=status)
        return task

    @classmethod
    def _load_name_and_status(cls, manager, task_id):
        task_file = cls._get_task_file(manager, task_id)
        if not os.path.exists(task_file):
            raise exceptions.BadTaskId("'%s' does not exist" % task_id)

        with open(task_file, "r") as f:
            lines = f.readlines()
            name = lines[0].rstrip('\n')
            status_line = lines[-1].rstrip('\n')
            status, timestamp = status_line.split(" ", 1)
        return name, status

    @classmethod
    def _generate_task_id(cls, name):
        date_str = utils.get_date_str(fmt="%Y_%m_%d")
        slug = cls._slugify(name)
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

    @classmethod
    def _get_task_file(cls, manager, task_id):
        """Return the file under tasks/year/month/day/slug for this task"""
        task_dir = cls._get_task_dir(manager, task_id)
        slug, year, month, day = cls._get_task_id_parts(task_id)
        task_file = os.path.join(task_dir, slug)
        return task_file

    def _append_task_file(self, line):
        task_file = self._get_task_file(self.manager, self.task_id)
        with open(task_file, "a") as f:
            f.write("%s\n" % line)

    def _append_status_timestamp(self):
        datetime_str = utils.get_datetime_str()
        timelog = "%s %s" % (self.status, datetime_str)
        self._append_task_file(timelog)

    def initialize_task(self):
        """Create the task in its inital state under the task/ dir"""
        task_dir = self._get_task_dir(self.manager, self.task_id)
        utils.mkdirs_easy(task_dir)
        self._append_task_file(self.name)
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
        task_file = self._get_task_file()
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

    def _parse_timelog(self):
        """Return timelog as list of (status, datetime) tuples"""
        status_dts = []
        task_file = self._get_task_file(self.manager, self.task_id)
        with open(task_file, "r") as f:
            lines = f.readlines()
            status_lines = lines[1:]
            for status_line in status_lines:
                status, timestamp = status_line.rstrip('\n').split(" ", 1)
                dt = utils.get_datetime_from_str(timestamp)
                status_dts.append((status, dt))
        return status_dts

    def get_duration(self):
        """Return the task duration in seconds.

        Duration is defined as the SUM((stop_time - start_time))
        """
        #FIXME: for now assume stopped
        status_dts = self._parse_timelog()
    
        total_secs = 0
        started = None
        for status, dt in status_dts:
            if status == "started":
                started = dt
            elif status == "stopped":
                stopped = dt
                timedelta = stopped - started
                delta_secs = utils.timedelta_total_seconds(timedelta)
                total_secs += delta_secs 
        
        return total_secs
