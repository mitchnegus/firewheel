from firewheel.lib.minimega.file_store import FileStore


class ImageStore(FileStore):
    """
    A repository for VM images that uses the minimega FileStore for easy access
    on all hosts in a Firewheel cluster.
    """

    def __init__(self, store: str = "images", decompress: bool = True) -> None:
        """Initialize the ImageStore.

        Args:
            store (str): The relative path from the minimega files directory
                for this FileStore. Defaults to "images".
            decompress (bool): Whether to decompress files by default when using
                this FileStore. Defaults to True.
        """
        super().__init__(store=store, decompress=decompress)

    def add_file(self, path: str, force: bool = True) -> bool:
        """Add an image file to the :py:class:`FileStore <firewheel.lib.minimega.file_store.FileStore>`.

        Args:
            path (str): The path of the file being transferred.
            force (bool): Whether to force adding the new image.
        """
        super().add_image_file(path, force=force)
