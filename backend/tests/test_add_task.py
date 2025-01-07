import unittest
import time
from celery import Celery
from celery.result import AsyncResult
from tasks import app
from tasks.tasks import add
import redis
import os

class TestAddTask(unittest.TestCase):
    def test_redis_connection(self):
        """
        Test the Redis connection.
        """
        try:
            client = redis.StrictRedis(host='localhost', port=6379, db=0)
            client.ping()
            print("Redis is accessible from the test.")
        except redis.ConnectionError as e:
            self.fail(f"Redis connection failed: {e}")

    def test_celery_connection(self):
        """
        Test Celery worker connection and basic task handling.
        """
        app = Celery('test', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

        try:
            # Send a simple test task to the worker
            result = app.send_task('tasks.tasks.add', args=(1, 2))
            print(f"Task sent successfully. Task ID: {result.id}")

            # Wait for the result
            task_result = AsyncResult(result.id)
            value = task_result.get(timeout=10)
            self.assertEqual(value, 3, f"Celery test task returned incorrect value: {value}")
            print("Celery worker connected and task processed successfully.")
        except Exception as e:
            self.fail(f"Celery connection test failed: {e}")

    def test_add_task(self):
        """
        Test the add Celery task.
        """
        # print("Add Task - Environment variables:")
        # for key, value in os.environ.items():
        #     print(f"{key}: {value}")

        result = add.delay(4, 6)  # Call the Celery task

        try:
            time.sleep(2)
            task_result = AsyncResult(result.id)  # Fetch the task result
            value = task_result.get(timeout=10)  # Get the result
            self.assertEqual(value, 10, f"Add task returned incorrect value: {value}")
            print("Test passed. Add task returned:", value)
        except Exception as e:
            self.fail(f"Add task failed with error: {e}")

if __name__ == "__main__":
    unittest.main()
