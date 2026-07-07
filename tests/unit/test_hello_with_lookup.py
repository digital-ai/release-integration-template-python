import pytest

from src.hello_with_lookup import HelloWithLookup


@pytest.fixture
def hello_with_lookup_task():
    """A fresh HelloWithLookup task instance for each test."""
    return HelloWithLookup()


@pytest.mark.parametrize(
    "name, expected_greeting",
    [
        ("Alice", "Hello Alice"),
        ("Benjamin", "Hello Benjamin"),
        ("Charlotte", "Hello Charlotte"),
    ],
)
def test_hello_with_lookup_greets_selected_name(
    hello_with_lookup_task, name, expected_greeting
):
    # Given
    hello_with_lookup_task.input_properties = {"task_id": "task_1", "yourName": name}

    # When
    hello_with_lookup_task.execute_task()

    # Then
    assert hello_with_lookup_task.get_output_properties()["greeting"] == expected_greeting


def test_hello_with_lookup_rejects_empty_name(hello_with_lookup_task):
    # Given
    hello_with_lookup_task.input_properties = {"task_id": "task_1", "yourName": ""}

    # When / Then
    with pytest.raises(ValueError, match="cannot be empty"):
        hello_with_lookup_task.execute()