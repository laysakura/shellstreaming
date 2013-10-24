# shellstreaming
A stream processor working with shell commands

## For developers

### Testing
```bash
$ ./setup.py nosetests
```

### Building and uploading documents
```bash
$ ./setup.py build_sphinx
$ ls doc/html/index.html
$ ./setup.py upload_sphinx
```

### Uploading packages to PyPI
```bash
$ emacs shellstreaming/__init__.py   # edit __version__
$ emacs CHANGES.txt
$ ./setup.py sdist upload
```

# TODO
- _internal_replをlistにしても動くことを確認するテスト
