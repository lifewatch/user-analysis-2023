# This file will contain all the classes and functions needed to complete
# the dereferencing process

import logging
import requests
from rdflib import Graph
from urllib.parse import urljoin
from html.parser import HTMLParser
import time
import re
from .graphdb import writeStoreToGraphDB, get_graph_from_trajectory

log = logging.getLogger(__name__)

REGEXP = r"(?:\w+:\w+|<[^>]+>)"  # r"(?<!^)(?<!<)/(?!@)(?![^<]*>)(?!$)"


class MyHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.links = []
        self.scripts = []
        self.in_script = False
        self.type = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and "rel" in attrs and attrs["rel"] == "describedby":
            if "href" in attrs:
                self.links.append(attrs["href"])
        elif (
            tag == "script"
            and "type" in attrs
            and (
                attrs["type"] == "application/ld+json" or attrs["type"] == "text/turtle"
            )
        ):
            self.in_script = True
            self.type = attrs["type"]

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False

    def handle_data(self, data):
        if self.in_script:
            self.scripts.append({self.type: data})


def download_uri_to_store(uri, store, format="json-ld"):
    # sleep for 1 second to avoid overloading any servers => TODO make this
    # configurable and add a warning + smart retry
    log.info(f"downloading {uri} to the store")
    time.sleep(1)
    headers = {"Accept": "application/ld+json, text/turtle"}
    r = requests.get(uri, headers=headers)

    # check if the request was successful and it returned a json-ld or ttl file
    if r.status_code == 200 and (
        "application/ld+json" in r.headers["Content-Type"]
        or "text/turtle" in r.headers["Content-Type"]
        or "application/json" in r.headers["Content-Type"]
    ):
        # parse the content directly into the store
        if (
            "application/ld+json" in r.headers["Content-Type"]
            or "application/json" in r.headers["Content-Type"]
        ):
            format = "json-ld"
        elif "text/turtle" in r.headers["Content-Type"]:
            format = "turtle"
        store.parse(data=r.text, format=format, publicID=uri)
        log.info(f"content of {uri} added to the store")
    else:
        # perform a check in the html to see if there is any link to fair signposting
        # perform request to uri with accept header text/html
        headers = {"Accept": "text/html"}
        r = requests.get(uri, headers=headers)
        if r.status_code == 200 and "text/html" in r.headers["Content-Type"]:
            # parse the html and check if there is any link to fair signposting
            # if there is then download it to the store
            log.info(f"content of {uri} is html")
            # go over the html file and find all the links in the head section
            # and check if there is any links with rel="describedby" anf if so
            # then follow it and download it to the store

            parser = MyHTMLParser()
            parser.feed(r.text)
            log.info(f"found {len(parser.links)} links in the html file")
            for link in parser.links:
                # check first if the link is absolute or relative
                if link.startswith("http"):
                    absolute_url = link
                else:
                    # Resolve the relative URL to an absolute URL
                    absolute_url = urljoin(uri, link)
                # download the uri to the store
                download_uri_to_store(absolute_url, store)
            for script in parser.scripts:
                # parse the script and check if it is json-ld or turtle
                # if so then add it to the store
                log.info(f"script: {script}")
                # { 'application/ld+json': '...'} | {'text/turtle': '...'}
                if "application/ld+json" in script:
                    log.info(f"found script with type application/ld+json")
                    store.parse(
                        data=script["application/ld+json"],
                        format="json-ld",
                        publicID=uri,
                    )
                elif "text/turtle" in script:
                    log.info(f"found script with type text/turtle")
                    store.parse(
                        data=script["text/turtle"], format="turtle", publicID=uri
                    )
            parser.close()
            return
        log.warning(
            f"request for {uri} failed with status code {r.status_code} and content type {r.headers['Content-Type']}"
        )


class SubTasks:
    def __init__(self, propertypaths: dict):
        self.tasks = propertypaths if propertypaths else []
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
        # do regex here to seperate the different elements from each other and
        # then make the currect parent task.
        matches = re.findall(REGEXP, task)
        p_task = matches[:-1]
        if len(p_task) == 0:
            log.warning(f"parent task is empty")
            return
        self.add_task("/".join(p_task))

    def reverse(self):
        """
        Reverse the tasks list
        """
        self.tasks.reverse()
        log.debug(f"tasks reversed: {self.tasks}")

    def run(self, graph, uri, prefixes):
        while self.__len__() > 0:
            last_failed_tasks = self.failed_tasks.copy()
            last_successful_tasks = self.successful_tasks.copy()
            log.debug(f"task length: {self.__len__()}")
            for task in self.tasks:
                # implode the array to a string with / as separator
                q_r = get_graph_from_trajectory(graph, uri, task, prefixes)

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
    def __init__(self, uri: str, propertypaths: dict, store: Graph, prefixes: dict):
        self.uri = uri
        self.store = store
        self.prefixes = prefixes
        log.info(f"prefixes: {self.prefixes}")
        self.subtasks = SubTasks(propertypaths)

        # download the uri to the store
        download_uri_to_store(uri, self.store)
        self.subtasks.run(self.store, self.uri, self.prefixes)
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
