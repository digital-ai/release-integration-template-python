import unittest

from src.hello import Hello


class TestHello(unittest.TestCase):

    def test_hello(self):

        # Given
        input_properties = {
            'task_id': 'task_1',
            'yourName': 'World'
        }
        task = Hello()
        task.input_properties = input_properties

        # When
        task.execute()

        # Then
        output_properties = task.get_output_properties()
        self.assertEqual(output_properties['greeting'], 'Hello World')


if __name__ == '__main__':
    unittest.main()
