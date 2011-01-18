import errno
import os

from tt import exceptions
from tt.task import Task

class TaskManager(object):

    def __init__(self, tt_dir):
        self.tt_dir = os.path.expanduser(tt_dir)

    def get_task_file(self, task):
        """Returns task file for given task"""
        task_file = task.get_task_file()
        return task_file

    def add_task(self, name):
        """This adds a task and adjusts the TaskManager state accordingly"""
        task = Task.create(manager=self, name=name, status="pending")
        task.initialize_task()
        return task

    def start_task(self, task):
        """Start a task, stopping the current one"""
        cur_task = self.get_started_task()
        if cur_task:
            cur_task.stop()

        task.start()

    def stop_current_task(self):
        cur_task = self.get_started_task()
        if not cur_task:
            raise exceptions.StatusChangeException("No started tasks")

        cur_task.stop()

    def delete_task(self, task):
        task.delete()

    def done_task(self, task):
        """Finish a task, if it's in progress, stop it, then finish it """
        if task.status == "started":
            task.stop()

        task.done()

    def close_done_tasks(self):
        """Close all done tasks"""
        tasks = self.get_tasks_by_status("done")
        for task in tasks:
            task.close()

    def initialize_state(self):
        """Creates a brand new instance of tt"""
        self._create_tt_dir()

    def get_started_task_id(self):
        task_ids = self.get_task_ids_by_status("started")
        task_id = task_ids[0] if task_ids else None
        return task_id

    def get_started_task(self):
        task_id = self.get_started_task_id()
        task = self.get_task(task_id) if task_id else None
        return task

    def get_task_ids_by_status(self, status):
        status_dir = self._get_status_dir(status)
        try:
            task_ids = os.listdir(status_dir)
        except OSError, e:
            if e.errno == errno.ENOENT:
                raise exceptions.DirectoryNotFound(
                    "'%s' not found" % status_dir)
            else:
                raise
        return task_ids

    def get_tasks_by_status(self, status):
        task_ids = self.get_task_ids_by_status(status)
        for task_id in task_ids:
            task = self.get_task(task_id)
            yield task

    def get_task(self, task_id):
        task = Task.load(self, task_id)
        return task

    def get_all_tasks(self):
        """Yields every task in the system"""
        tasks_dir = self._get_tasks_dir()
        for root, dirs, files in os.walk(tasks_dir):
            for file in files:
                task_file = os.path.join(root, file)
                task = Task.load_from_file(self, task_file)
                yield task

    def get_tasks_with_status_on_date(self, status, date):
        """Return tasks that have a timelog entry of the given status on the
        given date. `date` should be a datetime or datetime.date obj

        Since this scans all tasks, this is very expensive.
        """
        tasks = self.get_all_tasks()
        for task in tasks:
            entries = task.get_log_entries_for_date(date)
            statuses = [s for s, _ in entries]
            if status in statuses:
                yield task

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
    tasks/
        """
        os.makedirs(self.tt_dir)

        for status in Task.DIRECTORY_STATUSES:
            status_dir = self._get_status_dir(status)
            os.makedirs(status_dir)

        tasks_dir = self._get_tasks_dir()
        os.makedirs(tasks_dir)

    def _get_state_dir(self):
        state_dir = os.path.join(self.tt_dir, "state")
        return state_dir

    def _get_status_dir(self, status):
        state_dir = self._get_state_dir()
        status_dir = os.path.join(state_dir, "status", status)
        return status_dir

    def _get_tasks_dir(self):
        tasks_dir = os.path.join(self.tt_dir, "tasks")
        return tasks_dir
