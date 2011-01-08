import errno
import os
import datetime

def timedelta_total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def get_now():
    now = datetime.datetime.now()
    return now

def get_date_str(fmt=None):
    if fmt is None:
        fmt = "%Y-%m-%d"
    now = get_now()
    date_str = now.strftime(fmt)
    return date_str

def get_datetime_str():
    fmt = "%Y-%m-%d %H:%M:%S"
    return get_date_str(fmt=fmt)

def get_datetime_from_str(datetime_str):
    fmt = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.strptime(datetime_str, fmt)

def mkdirs_easy(dir):
    """mkdirs but don't raise if it exists"""
    try:
        os.makedirs(dir)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

class StatusChangeException(Exception):
    pass

class Task(object):
    STATUSES = ["pending", "started", "stopped", "done", "closed", "deleted"]
    
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
        with open(task_file, "r") as f:
            lines = f.readlines()
            name = lines[0].rstrip('\n')
            status_line = lines[-1].rstrip('\n')
            status, timestamp = status_line.split(" ", 1)
        return name, status

    @classmethod
    def _generate_task_id(cls, name):
        date_str = get_date_str(fmt="%Y_%m_%d")
        slug = cls._slugify(name)
        task_id = "%s-%s" % (slug, date_str)
        return task_id

    @classmethod
    def _get_task_id_parts(cls, task_id):
        """Return the components of a task_id"""
        slug, date_str = task_id.split("-")
        year, month, day = date_str.split("_")
        return (slug, year, month, day)

    @classmethod
    def _slugify(cls, name, max_len=16):
        INVALID_CHARS = ["/", ":", "-"]
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
        datetime_str = get_datetime_str()
        timelog = "%s %s" % (self.status, datetime_str)
        self._append_task_file(timelog)

    def initialize_task(self):
        """Create the task in its inital state under the task/ dir"""
        task_dir = self._get_task_dir(self.manager, self.task_id)
        mkdirs_easy(task_dir)
        self._append_task_file(self.name)
        self._initialize_task_status()

    def _initialize_task_status(self):
        """Add this task to the state/status/ table"""
        task_file = self._get_task_status_file()
        with open(task_file, "w") as f:
            f.write("")  # The files presence is all that matters

        self._append_status_timestamp()

    def _get_task_status_file(self):
        status_dir = self.manager._get_status_dir(self.status)
        task_file = os.path.join(status_dir, self.task_id)
        return task_file

    def _update_status(self, status):
        """Update state/status table and write timelog"""
        if status == self.status:
            raise StatusChangeException(
                "New status must be different than %s" % self.status)

        old_task_file = self._get_task_status_file()
        self.status = status
        new_task_file = self._get_task_status_file()
        os.rename(old_task_file, new_task_file)
        self._append_status_timestamp()

    def start(self):
        if self.status not in ("pending", "stopped"):
            raise StatusChangeException("Task must be pending or stopped")

        self._update_status("started")

    def stop(self):
        if self.status != "started":
            raise StatusChangeException("Task must be started")

        self._update_status("stopped")
    
    def done(self):
        if self.status != "stopped":
            raise StatusChangeException("Task must be stopped")

        self._update_status("done")

    def close(self):
        if self.status != "done":
            raise StatusChangeException("Task must be done")

        self._update_status("closed")

    def delete(self):
        if self.status == "closed":
            raise StatusChangeException("Task cannot be closed")

        self._update_status("deleted")

    def _parse_timelog(self):
        """Return timelog as list of (status, datetime) tuples"""
        status_dts = []
        task_file = self._get_task_file(self.manager, self.task_id)
        with open(task_file, "r") as f:
            lines = f.readlines()
            status_lines = lines[1:]
            for status_line in status_lines:
                status, timestamp = status_line.rstrip('\n').split(" ", 1)
                dt = get_datetime_from_str(timestamp)
                status_dts.append((status, dt))
        return status_dts

    def get_total_duration(self):
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
                delta_secs = timedelta_total_seconds(timedelta)
                total_secs += delta_secs 
        
        return total_secs

    def get_pretty_total_duration(self):
        """Return a human readable form of total duration"""
        total_secs = self.get_total_duration()
        #TODO: write code to go from secs -> min -> hours -> days -> weeks 
        # -> months -> years
        return "%s seconds" % total_secs

class TaskManager(object):
    TT_DIR = "/tmp/ttdata"


    def add_task(self, name):
        """This adds a task and adjusts the TaskManager state accordingly"""
        task = Task.create(manager=self, name=name, status="pending")
        task.initialize_task()
        return task

    def start_task(self, task):
        task.start()

    def stop_task(self, task):
        task.stop()

    def done_task(self, task):
        task.done()

    def initialize_state(self):
        """Creates a brand new instance of tt"""
        self._create_tt_dir()

    def get_task_ids_by_status(self, status):
        status_dir = self._get_status_dir(status)
        task_ids = os.listdir(status_dir)
        return task_ids

    def get_tasks_by_status(self, status):
        tasks = []
        task_ids = self.get_task_ids_by_status(status)
        for task_id in task_ids:
            task = self.get_task(task_id)
            tasks.append(task)
        return tasks

    def get_task(self, task_id):
        task = Task.load(self, task_id)
        return task

    def _create_tt_dir(self):
        """
.tt/
    ttconfig
    state/
        status/
            pending/
            started/
            stopped/
            done/
            closed/
            deleted/
    tasks/
        """
        tt_dir = self._get_tt_dir()

        os.makedirs(tt_dir)

        for status in Task.STATUSES:
            status_dir = self._get_status_dir(status)
            os.makedirs(status_dir)

        tasks_dir = self._get_tasks_dir()
        os.makedirs(tasks_dir)

    def _get_tt_dir(self):
        """Return TT's working directory"""
        tt_dir = os.path.expanduser(self.TT_DIR)
        return tt_dir

    def _get_state_dir(self):
        tt_dir = self._get_tt_dir()
        state_dir = os.path.join(tt_dir, "state")
        return state_dir

    def _get_status_dir(self, status):
        state_dir = self._get_state_dir()
        status_dir = os.path.join(state_dir, "status", status)
        return status_dir

    def _get_tasks_dir(self):
        tt_dir = self._get_tt_dir()
        tasks_dir = os.path.join(tt_dir, "tasks")
        return tasks_dir
