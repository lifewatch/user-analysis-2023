import unittest
from unittest.mock import patch, MagicMock
from lwua.ingest import run_ingest

class TestIngest(unittest.TestCase):
    @patch('ingest.get_registry_of_lastmod')
    @patch('ingest.FolderChangeDetector')
    @patch('ingest.IngestChangeObserver')
    def test_run_ingest(self, mock_observer, mock_detector, mock_lastmod):
        # Arrange
        mock_lastmod.return_value = None
        mock_detector_instance = mock_detector.return_value
        mock_detector_instance.report_changes.return_value = None
        mock_observer_instance = mock_observer.return_value

        # Act
        run_ingest()

        # Assert
        mock_lastmod.assert_called_once()
        mock_detector.assert_called_once()
        mock_observer.assert_called_once()
        mock_detector_instance.report_changes.assert_called()

if __name__ == '__main__':
    unittest.main()