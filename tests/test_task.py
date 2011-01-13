import datetime
import unittest

from tt import exceptions
from tt import task
from tt import task_manager
from tt import utils


class BaseTaskTest(unittest.TestCase):

    def setUp(self):
        tt_dir = "fakedir"
        self.manager = task_manager.TaskManager(tt_dir)

        self.task = task.Task.create(
            manager=self.manager,
            name="Develop tt sooner rather than later",
            status="pending")

        now = datetime.datetime(2011, 1, 7, 2, 0, 0, 0)  # 2:00
        utils.get_now = lambda: now


class TaskTest(BaseTaskTest):

    def test_generate_task_id(self):
        self.assertEqual(self.task.task_id, "develop_tt_soone-2011_01_07")

    def test_get_task_id_parts(self):
        task_id_parts = self.task._get_task_id_parts(self.task.task_id)
        self.assertEqual(task_id_parts,
                         ("develop_tt_soone", "2011", "01", "07"))


class GetDurationTest(BaseTaskTest):
    """Tests for Task.get_duration"""

    def make_log_entry(self, status, hhmmss):
        """Creates a timelog entry when given the status and time in HH:MM:SS
        format
        """
        hh, mm, ss = hhmmss.split(':')
        dt = datetime.datetime(2011, 1, 7, int(hh), int(mm), int(ss), 0)
        return (status, dt)

    def test_bounded_interval(self):
        entry = self.make_log_entry

        self.task.log = [
            entry('pending', '01:00:00'),
            entry('started', '01:10:00'),
            entry('stopped', '01:10:06')
        ]

        duration = self.task.get_duration()
        self.assertEqual(duration.seconds, 6)

    def test_two_bounded_intervals(self):
        entry = self.make_log_entry

        self.task.log = [
            entry('pending', '01:00:00'),
            entry('started', '01:10:00'),
            entry('stopped', '01:10:06'),
            entry('started', '01:10:10'),
            entry('stopped', '01:10:17')
        ]

        duration = self.task.get_duration()
        self.assertEqual(duration.seconds, 13)

    def test_unbounded_interval(self):
        entry = self.make_log_entry

        self.task.log = [
            entry('pending', '01:00:00'),
            entry('started', '01:10:00'),
        ]

        # 2:00 - 1:10 = 50 min = 3000 seconds
        duration = self.task.get_duration()
        self.assertEqual(duration.seconds, 3000)

    def test_invalid_interval1(self):
        """started with no stopped, started not last entry"""
        entry = self.make_log_entry

        self.task.log = [
            entry('pending', '01:00:00'),
            entry('started', '01:10:00'),
            entry('closed',  '01:11:00'),
        ]

        self.assertRaises(exceptions.StatusChangeException,
                          self.task.get_duration)

    def test_invalid_interval2(self):
        """'started' followed by a 'started'"""
        entry = self.make_log_entry

        self.task.log = [
            entry('pending', '01:00:00'),
            entry('started', '01:10:00'),
            entry('started', '01:11:00'),
        ]

        self.assertRaises(exceptions.StatusChangeException,
                          self.task.get_duration)


class GetDurationForDateTest(BaseTaskTest):
    """Tests for Task.get_duration_for_date"""

    def make_log_entry(self, status, datetime_str):
        """Creates a timelog entry when given the status and time in HH:MM:SS
        format
        """
        dt = utils.get_datetime_from_str(datetime_str)
        return status, dt

    def test_only_started_on_date(self):
        entry = self.make_log_entry
        self.task.log = [
            entry('pending', '2011-01-7 01:00:00'),
            entry('started', '2011-01-7 01:10:00'),
            entry('stopped', '2011-01-7 01:11:00'),
            entry('started', '2011-01-8 01:10:00'),
            entry('stopped', '2011-01-8 01:12:00')
        ]

        date = datetime.date(2011, 1, 7)
        duration = self.task.get_duration_for_date(date)

        msg = "(2011-01-7 01:11:00 - 2011-01-7 01:10:00) = 60 seconds"
        self.assertEqual(duration.seconds, 60, msg)


    def test_crosses_midnight(self):
        entry = self.make_log_entry
        self.task.log = [
            entry('pending', '2011-01-5 01:00:00'),
            entry('started', '2011-01-5 23:59:10'),
            entry('stopped', '2011-01-6 00:01:00')
        ]

        date = datetime.date(2011, 1, 5)
        duration = self.task.get_duration_for_date(date)

        msg = "(2011-01-6 00:00:00 - 2011-01-5 23:59:10) = 50 seconds"
        self.assertEqual(duration.seconds, 50, msg)

    def test_unbounded(self):
        entry = self.make_log_entry
        self.task.log = [
            entry('pending', '2011-01-7 01:00:00'),
            entry('started', '2011-01-7 01:59:30')
        ]

        date = datetime.date(2011, 1, 7)
        duration = self.task.get_duration_for_date(date)

        msg = "(2011-01-7 02:00:00 - 2011-01-07 01:59:30) = 30 seconds"
        self.assertEqual(duration.seconds, 30, msg)


if __name__ == "__main__":
    unittest.main()
