import unittest
import os
from testcontainers.compose import DockerCompose

class DockerTestSuite(unittest.TestSuite):
    def setUp(self):
        self.docker_compose = DockerCompose("../../../../", "docker-compose.yml")
        self.docker_compose.start()

    def tearDown(self):
        self.docker_compose.stop()

    def run(self, result=None):
        self.setUp()
        super(DockerTestSuite, self).run(result)
        self.tearDown()

if __name__ == "__main__":
    # Start test suite
    loader = unittest.TestLoader()
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    non_docker_suite = loader.discover(current_dir_path, pattern='test_*.py')
    suite = DockerTestSuite(loader.discover(current_dir_path, pattern='docker_test_*.py'))

    # Run the tests
    runner = unittest.TextTestRunner()
    runner.run(suite)
    runner.run(non_docker_suite)