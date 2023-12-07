# This file will contain all the classes and functions needed to complete
# the dereferencing process

import logging
import requests
from rdflib import Graph
import time
from .graphdb import writeStoreToGraphDB, get_graph_from_trajectory

log = logging.getLogger(__name__)


def download_uri_to_store(uri, store, format="json-ld"):
    # sleep for 1 second to avoid overloading any servers => TODO make this
    # configurable and add a warning + smart retry
    time.sleep(1)
    headers = {"Accept": "application/ld+json, text/turtle"}
    r = requests.get(uri, headers=headers)

    # check if the request was successful and it returned a json-ld or ttl file
    if r.status_code == 200 and (
        "application/ld+json" in r.headers["Content-Type"]
        or "text/turtle" in r.headers["Content-Type"]
    ):
        # parse the content directly into the store
        if "application/ld+json" in r.headers["Content-Type"]:
            format = "json-ld"
        elif "text/turtle" in r.headers["Content-Type"]:
            format = "turtle"
        store.parse(data=r.text, format=format)
        log.info(f"content of {uri} added to the store")
    else:
        log.warning(
            f"request for {uri} failed with status code {r.status_code} and content type {r.headers['Content-Type']}"
        )


def make_tasks(propertypaths):
    """
    Create tasks for all the propertypaths
    """
    tasks = []

    def helper(propertypath, task=[]):
        if isinstance(propertypath, dict):
            # property path is the key of the dict
            property_to_search = list(propertypath.keys())[0]
            return helper(
                propertypath[property_to_search],
                task + [property_to_search])
        elif isinstance(propertypath, str):
            tasks.append(task + [propertypath])
        else:
            for subpath in propertypath:
                helper(subpath, task)

    try:
        for propertypath in propertypaths:
            helper(propertypath)
    except Exception as e:
        log.error(f"Error creating tasks: {e}")
        tasks = []

    return tasks


class SubTasks:
    def __init__(self, propertypaths: dict):
        self.tasks = make_tasks(propertypaths)
        self.failed_tasks = []
        self.last_failed_tasks = []
        self.last_successful_tasks = []
        self.successful_tasks = []

    def __repr__(self):
        return f"SubTasks({self.tasks})"

    def __iter__(self):
        return iter(self.tasks)

    def __len__(self):
        return len(self.tasks)

    def add_failed_task(self, task: list):
        """
        Add a task to the failed tasks list
        """
        # check if the task is already in the list
        if task in self.failed_tasks:
            log.warning(f"task {task} already in failed tasks")
            return
        self.failed_tasks.append(task)

    def delete_task(self, task: list):
        """
        Delete a task from the tasks list based on its value
        """
        if task in self.tasks:
            self.tasks.remove(task)
            return
        log.warning(f"subtask {task} not found in subtasks")

    def add_task(self, task: list):
        """
        Add a task to the tasks list
        """
        # check if the task is already in the list
        if task in self.tasks:
            log.warning(f"task {task} already in tasks")
            return
        self.tasks.append(task)

    def add_parent_task(self, task: list):
        """
        Deletes the task given but adds a different task based on the parent task
        :param task: the task to delete
        :type task: list
        """
        p_task = task[:-1]
        if len(p_task) == 0:
            log.warning(f"parent task is empty")
            return
        self.add_task(p_task)

    def reverse(self):
        """
        Reverse the tasks list
        """
        self.tasks.reverse()

    def run(self, graph, uri):
        while self.__len__() > 0:
            last_failed_tasks = self.failed_tasks.copy()
            last_successful_tasks = self.successful_tasks.copy()
            log.debug(f"task length: {self.__len__()}")
            for task in self.tasks:
                # implode the array to a string with / as separator
                q_r = get_graph_from_trajectory(graph, uri, task)

                # check if the query returned any results and if so then
                # continue to the next task , delete the task from the subtasks
                if len(q_r) > 0:
                    log.info(f"query returned {len(q_r)} results")
                    # for uri found , download it to the store
                    for uri in q_r:
                        download_uri_to_store(uri, graph)
                    self.successful_tasks.append(task)
                    self.delete_task(task)
                    continue
                # if result is 0 then create a new task for the parent path
                else:
                    log.info(f"query returned 0 results")
                    self.add_parent_task(task)
                    self.add_failed_task(task)
            # reverse the tasks list
            self.reverse()
            log.debug(f"last failed tasks: {last_failed_tasks}")
            log.debug(f"failed tasks: {self.failed_tasks}")

            # if the failed tasks list is the same as the last failed tasks list
            # and the successful tasks list is the same as the last successful tasks list
            # then break the loop

            if (
                self.failed_tasks == last_failed_tasks
                and self.successful_tasks == last_successful_tasks
            ):
                log.warning(f"failed tasks: {self.failed_tasks}")
                log.warning(f"successful tasks: {self.successful_tasks}")
                log.warning(f"tasks left: {self.tasks}")
                log.warning(f"breaking loop")
                break


class DerefUriEntity:
    def __init__(self, uri: str, propertypaths: dict, store: Graph):
        self.uri = uri
        self.store = store
        self.subtasks = SubTasks(propertypaths)

        # download the uri to the store
        download_uri_to_store(uri, self.store)
        self.subtasks.run(self.store, self.uri)
        self.propertypathmetadata = None
        self.propertypaths = propertypaths
        log.info(f"FINAL store length: {len(self.store)}")

    def __repr__(self):
        return f"DerefUriEntity({self.uri},{self.propertypaths},{self.store})"

    def write_store(self, filename):
        """
        Write the store to the graph database
        """
        log.info("writing store to graph database")
        writeStoreToGraphDB(self.store, filename)