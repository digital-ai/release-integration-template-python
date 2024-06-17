import unittest

from src.sample_server_task import ServerQuery


class TestServerQuery(unittest.TestCase):

    def test_server_query(self):

        # Given
        task = ServerQuery()
        task.input_properties = {
            'task_id': 'task_1',
            'productId': '123',
            'server': {
                'url': 'https://dummyjson.com',
                'username': 'admin',
                'password': 'admin',
                'authenticationMethod': 'Basic'
            }
        }

        # When
        task.execute_task()

        # Then
        self.assertEqual(task.get_output_properties()['productName'], 'iPhone 13 Pro')


if __name__ == '__main__':
    unittest.main()
