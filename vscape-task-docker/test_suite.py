import executor_test
import task_test
import unittest


runner = unittest.TextTestRunner()
runner.run(registry_test.suite())
runner.run(executor_test.suite())
runner.run(task_test.suite())


