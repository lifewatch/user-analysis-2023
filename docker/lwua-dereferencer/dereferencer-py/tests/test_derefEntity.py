# testfile for the derefEntity class

import pytest
from pathlib import Path
from dereferencer.derefEntity import (
    DerefUriEntity,
    SubTasks,
    make_tasks,
    download_uri_to_store,
)
from rdflib import Graph

# fake variables
# fake uri
uri = "http://marineregions.org/mrgid/17585"
# fake propertypaths
pp = ["http://www.example.org/property1", "http://www.example.org/property2"]
# fake store
store = Graph()


# DerefUriEntity tests
class TestDerefUriEntity:
    @pytest.fixture
    def deref_uri_entity(self):
        # Setup
        deref_uri_entity = DerefUriEntity(uri, pp, store)
        yield deref_uri_entity

    def test_deref_uri_entity_initialization(self, deref_uri_entity):
        # Assert that deref_uri_entity.uri is equal to uri
        assert deref_uri_entity.uri == uri
        # Assert that deref_uri_entity.store is of type Graph
        assert isinstance(deref_uri_entity.store, Graph)
        # Assert that deref_uri_entity.subtasks is of type SubTasks
        assert isinstance(deref_uri_entity.subtasks, SubTasks)
        # Assert that deref_uri_entity.subtasks.successful_tasks is empty
        assert deref_uri_entity.subtasks.successful_tasks == []


def test_make_tasks():
    # Arrange
    pp = ["http://www.example.org/property1",
          "http://www.example.org/property2"]
    # Act
    result = make_tasks(pp)
    # Assert
    assert result == [
        ["http://www.example.org/property1"],
        ["http://www.example.org/property2"],
    ]


def test_make_tasks_empty():
    # Arrange
    pp = []
    # Act
    result = make_tasks(pp)
    # Assert
    assert result == []


def test_make_tasks_object():
    # Arrange
    pp = [
        "http://www.example.org/property1",
        "http://www.example.org/property2",
        {
            "http://www.example.org/property3": [
                "http://www.example.org/property4",
                "http://www.example.org/property5",
            ]
        },
    ]
    # Act
    result = make_tasks(pp)
    # Assert
    assert result == [
        ["http://www.example.org/property1"],
        ["http://www.example.org/property2"],
        ["http://www.example.org/property3", "http://www.example.org/property4"],
        ["http://www.example.org/property3", "http://www.example.org/property5"],
    ]


TEST_URI_CASES = {
    "http://marineregions.org/mrgid/17585": True,
    "http://example.org/": False,
    "https://data.arms-mbon.org/": True,
}


def test_download_uri_to_store_cases():
    for uri, expected in TEST_URI_CASES.items():
        graph = Graph()
        result = download_uri_to_store(uri, graph)
        if expected:
            assert result is None
            assert len(graph) != 0
        else:
            assert len(graph) == 0


# tests for Subtasks class
class TestSubTasks:
    @pytest.fixture
    def subtasks(self):
        # Setup
        pp = [
            "http://www.example.org/property1",
            "http://www.example.org/property2",
            {
                "http://www.example.org/property3": [
                    "http://www.example.org/property4",
                    "http://www.example.org/property5",
                ]
            },
        ]
        subtasks = SubTasks(pp)
        yield subtasks

    def test_subtasks_initialization(self, subtasks):
        # Assert
        assert subtasks.failed_tasks == []
        assert subtasks.successful_tasks == []
        assert subtasks.last_failed_tasks == []
        assert subtasks.last_successful_tasks == []

    def test_subtasks_add_task(self, subtasks):
        # Act
        subtasks.add_task(["http://www.example.org/property7"])

        # Assert
        # Assert if task not in tasks
        assert ["http://www.example.org/property7"] in subtasks.tasks

    def test_subtasks_add_failed_task(self, subtasks):
        # Act
        subtasks.add_failed_task(["http://www.example.org/property7"])

        # Assert
        # Assert if task not in failed_tasks
        assert ["http://www.example.org/property7"] in subtasks.failed_tasks

    def test_delete_task(self, subtasks):
        # Act
        subtasks.delete_task(["http://www.example.org/property1"])
        # Assert
        # Assert if task in tasks
        assert ["http://www.example.org/property1"] not in subtasks.tasks

    def test_reverse(self, subtasks):
        # Act
        subtasks.reverse()
        # Assert
        # Assert if tasks is reversed
        assert subtasks.tasks == [
            ["http://www.example.org/property3", "http://www.example.org/property5"],
            ["http://www.example.org/property3", "http://www.example.org/property4"],
            ["http://www.example.org/property2"],
            ["http://www.example.org/property1"],
        ]

    def test_len(self, subtasks):
        # Act
        result = len(subtasks)
        # Assert
        # Assert if len of tasks is 4
        assert result == 4

    def test_add_parent_task_normal(self, subtasks):
        # Act
        subtasks.add_parent_task(
            [
                "http://www.example.org/property/parent",
                "http://www.example.org/property2",
            ]
        )
        # Assert
        # Assert if task in tasks
        assert ["http://www.example.org/property/parent"] in subtasks.tasks

    def test_add_parent_task_empty(self, subtasks):
        # Act
        subtasks.add_parent_task(["http://www.example.org/property2"])
        # Assert
        # Assert if task in tasks
        assert [] not in subtasks.tasks
