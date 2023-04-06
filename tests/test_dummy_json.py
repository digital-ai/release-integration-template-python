import unittest

from src.dummy_json import DummyJson


class TestDummyJson(unittest.TestCase):

    def test_dummy_json(self):

        # Given
        server = {
            'url': 'https://dummyjson.com',
            'username': 'admin',
            'password': 'admin',
            'authenticationMethod': 'Basic'
        }
        input_properties = {
            'task_id': 'task_1',
            'productId': '1',
            'server': server
        }
        task = DummyJson()
        task.input_properties = input_properties
        # When
        task.execute()

        # Then
        output_properties = task.get_output_properties()
        self.assertEqual(output_properties['productName'], 'iPhone 9')


if __name__ == '__main__':
    unittest.main()
