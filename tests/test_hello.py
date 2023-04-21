import unittest

from src.hello import Hello


class TestHello(unittest.TestCase):

    def test_hello(self):

        # Given
        task = Hello()
        task.input_properties = {
            'task_id': 'task_1',
            'yourName': 'World'
        }

        # When
        task.execute_task()

        # Then
        self.assertEqual(task.get_output_properties()['greeting'], 'Hello World')


if __name__ == '__main__':
    unittest.main()
