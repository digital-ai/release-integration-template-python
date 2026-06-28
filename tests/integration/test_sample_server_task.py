import pytest

from src.sample_server_task import ServerQuery


@pytest.mark.integration
def test_server_query():
    """Integration test: queries the live https://dummyjson.com service over the network."""
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
    assert task.get_output_properties()['productName'] == 'iPhone 13 Pro'
