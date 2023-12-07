# pytest file for testing all the things that can go wrong with the yaml config file

import pytest
import yaml
from pathlib import Path
from rdflib import Graph
from dereferencer.dereference import DerefTask, Dereference, isExpired
from datetime import datetime, timedelta


# fake config_path_from_config function
def config_path_from_config():
    return config_folder

# fake config folder
current_dir = Path(__file__).parent
config_folder = current_dir /  "config_files"

# isExpired tests
def test_is_expired_true():
    # Arrange
    past_time = datetime.now() - timedelta(days=1)

    # Act
    result = isExpired(past_time, 1)

    # Assert
    assert result == True

def test_is_expired_false():
    # Arrange
    future_time = datetime.now() + timedelta(days=1)

    # Act
    result = isExpired(future_time, 180)

    # Assert
    assert result == False

def test_is_expired_edge_case():
    # Arrange
    current_time = datetime.now()

    # Act
    result = isExpired(current_time, 1)

    # Assert
    assert result == False
    
# Dereftask tests
class TestDereferenceGoodConfig:
    @pytest.fixture
    def deref_task(self):
        # Setup
        path = config_folder / 'dereference_test_1.yml'
        deref_task = DerefTask(path)
        yield deref_task

    def test_dereftask_initialization(self, deref_task):
        
        # Assert that dref_task.store is of type Graph
        assert isinstance(deref_task.store, Graph)
        
        # Assert that deref_task.cache_lifetime is of type int and 180
        assert isinstance(deref_task.cache_lifetime, int)
        assert deref_task.cache_lifetime == 180
        
        # Assert that deref_task.uris is of type list and has 3 items
        assert isinstance(deref_task.uris, list)
        assert len(deref_task.uris) == 3
        
        # Assert that deref_task.deref_paths is of type object
        assert isinstance(deref_task.deref_paths, object)

class TestDereferenceBadConfig:
    @pytest.fixture
    def deref_task(self):
        # Setup
        path = config_folder / 'dereference_test_4.yml'
        
        # the deref task should fail
        try:
            deref_task = DerefTask(path)
            pytest.fail("DerefTask did not raise an exception")
        except Exception:
            pass

class TestDereferenceBadConfigTwo:
    @pytest.fixture
    def deref_task(self):
        # Setup
        path = config_folder / 'nested_folder/dereference_test_5.yml'
        
        # the deref task should fail
        try:
            deref_task = DerefTask(path)
            pytest.fail("DerefTask did not raise an exception")
        except Exception:
            pass
