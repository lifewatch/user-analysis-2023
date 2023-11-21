import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import lwua.graphdb as graphdb

class TestGraphDB(unittest.TestCase):
    @patch('graphdb.suffix_2_format')
    @patch('graphdb.Graph')
    def test_read_graph(self, mock_graph, mock_suffix_2_format):
        # Arrange
        mock_suffix_2_format.return_value = 'xml'
        mock_graph_instance = mock_graph.return_value
        mock_graph_instance.parse.return_value = None

        # Act
        result = graphdb.read_graph(Path('test.xml'))

        # Assert
        mock_suffix_2_format.assert_called_once_with('.xml')
        mock_graph.assert_called_once()
        mock_graph_instance.parse.assert_called_once_with(location='test.xml', format='xml')
        self.assertIsNone(result)

    @patch('graphdb.fname_2_context')
    @patch('graphdb.log.info')
    @patch('graphdb.assert_context_exists')
    @patch('graphdb.delete_graph')
    @patch('graphdb.update_registry_lastmod')
    def test_delete_data_file(self, mock_update_registry_lastmod, mock_delete_graph, mock_assert_context_exists, mock_log_info, mock_fname_2_context):
        # Arrange
        mock_fname_2_context.return_value = 'context'

        # Act
        graphdb.delete_data_file('test.xml')

        # Assert
        mock_fname_2_context.assert_called_once_with('test.xml')
        mock_log_info.assert_called_once()
        mock_assert_context_exists.assert_called_once_with('context')
        mock_delete_graph.assert_called_once_with('context')
        mock_update_registry_lastmod.assert_called_once_with('context', None)

if __name__ == '__main__':
    unittest.main()