# shellstreaming
A stream processor working with shell commands

## For developers

### API documents
Sphinx-powered documents are available on http://packages.python.org/shellstreaming/


### Building and uploading documents
```bash
$ ./setup.py build_sphinx
$ ls doc/html/index.html
$ ./setup.py upload_sphinx
```

### Testing
```bash
$ ./setup.py nosetests
```

### Uploading packages to PyPI
```bash
$ emacs shellstreaming/__init__.py   # edit __version__
$ emacs CHANGES.txt
$ ./setup.py sdist upload
```

# TODO
- _internal_replをlistにしても動くことを確認するテスト
