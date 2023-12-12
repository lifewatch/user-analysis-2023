# testfile for the derefEntity class

import pytest
from pathlib import Path
from dereferencer.derefEntity import (
    DerefUriEntity,
    SubTasks,
    download_uri_to_store,
    REGEXP,
)
import re
from rdflib import Graph

# fake variables
# fake uri
uri = "http://marineregions.org/mrgid/17585"
# fake propertypaths
pp = ["ex:lol", "<http://www.example.org/property2>"]
prefixes = {"ex": "<http://example.org/>"}
# fake store
store = Graph()


# DerefUriEntity tests
class TestDerefUriEntity:
    @pytest.fixture
    def deref_uri_entity(self):
        # Setup
        deref_uri_entity = DerefUriEntity(uri, pp, store, prefixes)
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


TEST_URI_CASES = {
    "http://marineregions.org/mrgid/17585": True,
    "http://example.org/": False,
    "https://data.arms-mbon.org/": True,
    "https://edmo.seadatanet.org/report/422": True,
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
            "mr:hasGeometry",
            "mr:isPartOf / mr:hasGeometry",
            "mr:isPartOf / <https://schema.org/geo> / <https://schema.org/latitude>",
            "mr:isPartOf/ <https://schema.org/geo>/<https://schema.org/longitude>",
            "mr:isPartOf/mr:hasGeometry    / <https://schema.org/latitude> /<https://schema.org/longitude>",
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
        subtasks.add_task("http://www.example.org/property7")

        # Assert
        # Assert if task not in tasks
        assert "http://www.example.org/property7" in subtasks.tasks

    def test_subtasks_add_failed_task(self, subtasks):
        # Act
        subtasks.add_failed_task("http://www.example.org/property7")

        # Assert
        # Assert if task not in failed_tasks
        assert "http://www.example.org/property7" in subtasks.failed_tasks

    def test_delete_task(self, subtasks):
        # Act
        subtasks.delete_task("http://www.example.org/property1")
        # Assert
        # Assert if task in tasks
        assert "http://www.example.org/property1" not in subtasks.tasks

    def test_reverse(self, subtasks):
        # Act
        subtasks.reverse()
        # Assert
        # Assert if tasks is reversed
        assert subtasks.tasks == [
            "mr:isPartOf/mr:hasGeometry    / <https://schema.org/latitude> /<https://schema.org/longitude>",
            "mr:isPartOf/ <https://schema.org/geo>/<https://schema.org/longitude>",
            "mr:isPartOf / <https://schema.org/geo> / <https://schema.org/latitude>",
            "mr:isPartOf / mr:hasGeometry",
            "mr:hasGeometry",
        ]

    def test_len(self, subtasks):
        # Act
        result = len(subtasks)
        # Assert
        # Assert if len of tasks is 5
        assert result == 5

    def test_add_parent_task_normal(self, subtasks):
        # Act
        subtasks.add_parent_task(
            "<http://www.example.org/property/parent> / <http://www.example.org/property2>"
        )
        # Assert
        # Assert if task in tasks
        assert "<http://www.example.org/property/parent>" in subtasks.tasks

    def test_add_parent_task_empty(self, subtasks):
        # Act
        subtasks.add_parent_task("<http://www.example.org/property2>")
        # Assert
        # Assert if task in tasks
        assert [] not in subtasks.tasks


# tests here for the regular expression that is used to seperate the
# different elements from each other in teh property path

to_test_strings = [
    "mr:hasGeometry",
    "mr:isPartOf / mr:hasGeometry",
    "mr:isPartOf / <https://schema.org/geo> / <https://schema.org/latitude>",
    "mr:isPartOf/ <https://schema.org/geo>/<https://schema.org/longitude>",
    "mr:isPartOf/mr:hasGeometry    / <https://schema.org/latitude> /<https://schema.org/longitude>",
    "mr:isPartOf/mr:hasGeometry   @ <https://schema.org/latitude> @ <https://schema.org/longitude>",
    "/mr:isPartOf/mr:hasGeometry   / <https://schema.org/latitude> / <https://schema.org/longitude>/"
    "",
    """"""
    "/mr:isPartOf/mr:hasGeometry  @@"
    "@@/@"
    " / <https://schema.org/latitude> / <https://schema.org/longitude>/"
    "",
]

expected_results = [["mr:hasGeometry"],
                    ["mr:isPartOf",
                     "mr:hasGeometry"],
                    ["mr:isPartOf",
                     "<https://schema.org/geo>",
                     "<https://schema.org/latitude>"],
                    ["mr:isPartOf",
                     "<https://schema.org/geo>",
                     "<https://schema.org/longitude>"],
                    ["mr:isPartOf",
                     "mr:hasGeometry",
                     "<https://schema.org/latitude>",
                     "<https://schema.org/longitude>",
                     ],
                    ["mr:isPartOf",
                     "mr:hasGeometry",
                     "<https://schema.org/latitude>",
                     "<https://schema.org/longitude>",
                     ],
                    ["mr:isPartOf",
                     "mr:hasGeometry",
                     "<https://schema.org/latitude>",
                     "<https://schema.org/longitude>",
                     ],
                    ["mr:isPartOf",
                     "mr:hasGeometry",
                     "<https://schema.org/latitude>",
                     "<https://schema.org/longitude>",
                     ],
                    ]


def test_regexp():
    for i in range(len(to_test_strings)):
        print(re.findall(REGEXP, to_test_strings[i]))
        assert re.findall(REGEXP, to_test_strings[i]) == expected_results[i]
