import unittest

from digitalai.release.integration import OutputContext
from src.dummy_json import DummyJson


class TestDummyJson(unittest.TestCase):

    def test_dummy_json(self):

        # Given
        task = DummyJson()
        task.input_properties = {
            'task_id': 'task_1',
            'productId': '1',
            'server': {
                'url': 'https://dummyjson.com',
                'username': 'admin',
                'password': 'admin',
                'authenticationMethod': 'Basic'
            }
        }
        task.output_context = OutputContext(0, "", {}, [])

        # When
        task.execute()

        # Then
        self.assertEqual(task.get_output_properties()['productName'], 'iPhone 9')


if __name__ == '__main__':
    unittest.main()
