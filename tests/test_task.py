import datetime
import unittest

import tt

class TaskTest(unittest.TestCase):
    def setUp(self):
        now = datetime.datetime(2011, 1, 7, 18, 53, 45, 796977)
        tt.get_now = lambda: now

        self.manager = tt.TaskManager()
        self.task = tt.Task.create(
            manager=self.manager,
            name="Develop tt sooner rather than later", status="pending",
            priority="high")

    def test_generate_task_id(self):
        self.assertEqual(self.task.task_id, "develop_tt_soone-2011_01_07")

    def test_get_task_id_parts(self):
        task_id_parts = self.task._get_task_id_parts()
        self.assertEqual(task_id_parts,
                         ("develop_tt_soone", "2011", "01", "07"))

    def test_get_task_dir(self):
        task_dir = self.task._get_task_dir()
        print task_dir

if __name__ == "__main__":
    unittest.main()
