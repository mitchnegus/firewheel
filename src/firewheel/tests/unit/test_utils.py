# pylint: disable=invalid-name

from firewheel.config import config
from firewheel.control.repository_db import RepositoryDb
from firewheel.lib.grpc.firewheel_grpc_client import FirewheelGrpcClient


def initalize_repo_db():
    repo_client = FirewheelGrpcClient(
        hostname=config["grpc"]["hostname"],
        port=config["grpc"]["port"],
        db=config["test"]["grpc_db"],
    )
    repo_client.remove_all_repositories()
    repository_db = RepositoryDb(
        host=config["grpc"]["hostname"],
        port=config["grpc"]["port"],
        db=config["test"]["grpc_db"],
    )
    return repository_db, repo_client


# pylint: disable=unused-argument
def cleanup_repo_db(repository_db, repo_client):
    repo_client.remove_all_repositories()


def compare_graph_structures(a, b):
    if "nodes" not in a or "edges" not in a:
        raise ValueError("First structure is not a valid graph structure.")
    if "nodes" not in b or "edges" not in b:
        raise ValueError("Second structure is not a valid graph structure.")

    for n in a["nodes"]:
        found = False
        for m in b["nodes"]:
            if n == m:
                found = True
                break
        if not found:
            return False
    for m in b["nodes"]:
        found = False
        for n in a["nodes"]:
            if n == m:
                found = True
                break
        if not found:
            return False

    for n in a["edges"]:
        found = False
        for m in b["edges"]:
            if n == m:
                found = True
                break
        if not found:
            return False
    for m in b["edges"]:
        found = False
        for n in a["edges"]:
            if n == m:
                found = True
                break
        if not found:
            return False

    for key in a:
        if key in ("nodes", "edges"):
            continue
        try:
            if a[key] != b[key]:
                return False
        except KeyError:
            return False
    for key in b:
        if key in ("nodes", "edges"):
            continue
        try:
            # No need to compare here--if the key exists in both a and b, then
            # it will already have been checked in the previous loop checking
            # a's keys. We just want to make sure that the key we found in b
            # also exists in a.
            a[key]
        except KeyError:
            return False

    return True
