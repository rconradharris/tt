import unittest

from tt import task_manager

class TaskManagerTest(unittest.TestCase):
    def setUp(self):
        self.task_manager = task_manager.TaskManager()
        #self.task_manager.initialize_state()

    def tearDown(self):
        pass

    def test_get_tt_dir(self):
       print self.task_manager._get_tt_dir()


if __name__ == "__main__":
    unittest.main()
