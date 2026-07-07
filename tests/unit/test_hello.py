import pytest

from src.hello import Hello


@pytest.fixture
def hello_task():
    """A fresh Hello task instance for each test."""
    return Hello()


@pytest.mark.parametrize(
    "name, expected_greeting",
    [
        ("World", "Hello World"),
        ("Ada", "Hello Ada"),
        ("Digital.ai", "Hello Digital.ai"),
    ],
)
def test_hello_greets_name(hello_task, name, expected_greeting):
    # Given
    hello_task.input_properties = {'task_id': 'task_1', 'yourName': name}

    # When
    hello_task.execute_task()

    # Then
    assert hello_task.get_output_properties()['greeting'] == expected_greeting


def test_hello_rejects_empty_name(hello_task):
    # Given
    hello_task.input_properties = {'task_id': 'task_1', 'yourName': ''}

    # When / Then
    with pytest.raises(ValueError, match="cannot be empty"):
        hello_task.execute()
