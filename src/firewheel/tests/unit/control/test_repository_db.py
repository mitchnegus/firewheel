
import pytest

from firewheel.config import config
from firewheel.control.repository_db import RepositoryDb
from firewheel.lib.grpc.firewheel_grpc_client import FirewheelGrpcClient


def create_test_repo(repo_path):
    repo_path.mkdir()
    return str(repo_path)


@pytest.fixture
def repo_entry(tmp_path):
    return {"path": create_test_repo(tmp_path / "test_repo")}


@pytest.fixture
def repo_entries(tmp_path):
    return [{"path": create_test_repo(tmp_path / f"test_repo_{_}")} for _ in range(2)]


@pytest.fixture
def grpc_client():
    grpc_client = FirewheelGrpcClient(
        hostname=config["grpc"]["hostname"],
        port=config["grpc"]["port"],
        db=config["test"]["grpc_db"],
    )
    grpc_client.remove_all_repositories()
    yield grpc_client
    grpc_client.remove_all_repositories()


@pytest.fixture
def repository_db():
    repository_db = RepositoryDb(
        host=config["grpc"]["hostname"],
        port=config["grpc"]["port"],
        db=config["test"]["grpc_db"],
    )
    yield repository_db
    repository_db.close()


class TestRepositoryDb:
    """Test the ``RepositoryDb`` object."""

    @staticmethod
    def _entry_matches_repo_dict(repo_entry, repo_dict):
        path = repo_entry["path"]
        return path == repo_dict[path]["path"]

    def test_repository_db_without_grpc_client(self):
        assert RepositoryDb(host=None, port=None, db=None).grpc_client is None

    def test_add_repository(self, grpc_client, repository_db, repo_entry):
        repository_db.add_repository(repo_entry)
        repo_dict = grpc_client.get_repositories_as_dict()
        assert len(repo_dict) == 1
        assert self._entry_matches_repo_dict(repo_entry, repo_dict)

    @pytest.mark.parametrize(
        ["invalid_entry", "exception"],
        [
            # Test invalid directory structures
            [
                {
                    "path": "/tmp/test-invalid",  # nosec
                    "invalid": "value",
                },
                KeyError,
            ],  # ----------------------------------------- too many keys
            [{"invalid": "value"}, KeyError],  # ---------- wrong key
            [{"path": "/root"}, PermissionError],  # ------ bad permissions
            [{"path": "asdf"}, FileNotFoundError],  # ----- missing directory
        ],
    )
    def test_add_repository_invalid(self, invalid_entry, exception, repository_db):
        with pytest.raises(exception):
            repository_db.add_repository(invalid_entry)

    def test_duplicate_repository(self, grpc_client, repository_db, repo_entry):
        repository_db.add_repository(repo_entry)
        repository_db.add_repository(repo_entry)
        repo_dict = grpc_client.get_repositories_as_dict()
        assert len(repo_dict) == 1
        assert self._entry_matches_repo_dict(repo_entry, repo_dict)

    def test_delete_repository(self, grpc_client, repository_db, repo_entry):
        repository_db.add_repository(repo_entry)
        repository_db.delete_repository(repo_entry)
        assert not list(grpc_client.list_repositories())

    def test_list_repositories(self, repository_db, repo_entries):
        orig_entry_count = len(list(repository_db.list_repositories()))
        for entry in repo_entries:
            repository_db.add_repository(entry)
        repo_list = list(repository_db.list_repositories())
        assert len(repo_list) == orig_entry_count + len(repo_entries)
