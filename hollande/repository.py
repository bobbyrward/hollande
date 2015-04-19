from .application import app


def parse_repo_string(repo_string):
    """Parse a repository string in the format "owner/name"

    :param repo_string: the repository
    :type repo_string: str
    """
    if '/' not in repo_string:
        raise ValueError(
            'Repo string "{}" is not a valid format'.format(repo_string)
        )

    return repo_string.split('/', 1)


class Repository(object):
    """A github repository """

    def __init__(self, repo_string):
        self.owner, self.name = parse_repo_string(repo_string)
        self.gh3_repo = app().github.repository('inmar', 'dpn_web_services')

    def get_file_hash_from_tree(self, tree, path_parts):
        if not isinstance(path_parts, list):
            path_parts = path_parts.split('/')

        this_path, sub_path = path_parts[0], path_parts[1:]

        for hash_object in tree.tree:
            if hash_object.path == this_path:
                if sub_path:
                    return self.get_file_hash_from_tree(
                        self.tree(hash_object.sha),
                        sub_path,
                    )
                else:
                    return hash_object

        raise KeyError('Unable to find path "{}"'.format(this_path))

    def blob(self, *args, **kwargs):
        return self.gh3_repo.blob(*args, **kwargs)

    def tree(self, *args, **kwargs):
        return self.gh3_repo.tree(*args, **kwargs)

    @property
    def active_pull_requests(self):
        return self.gh3_repo.iter_pulls(state='open')
