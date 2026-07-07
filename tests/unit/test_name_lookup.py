from src.name_lookup import LOOKUP_NAMES, NameLookup


def test_name_lookup_returns_dropdown_options():
    # Given
    task = NameLookup()
    task.input_properties = {
        "task_id": "task_1",
        "_ci": {},
        "_attributes": {},
        "_parameters": {},
    }

    # When
    task.execute_task()

    # Then
    expected_options = [{"label": name, "value": name} for name in LOOKUP_NAMES]
    assert task.get_output_properties()["commandResponse"] == expected_options
    assert all(set(option) == {"label", "value"} for option in expected_options)