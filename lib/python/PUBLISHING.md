# Publishing the Python package, not yet published

This package is prepared, not published. Do not run the upload
commands below until the format 1.0 publication is decided and the
package name is confirmed at upload time. The package version is
0.1.0, while the format is 1.0 Draft, because the package itself
has not had a 1.0 release yet. When the format is published, the
package version can move to 1.0.0 in a separate release, or stay
on its own version line with a note in the changelog. The two
versions are related, not identical: the format version lives in
the format field of every pack, the package version lives in
pyproject.toml.

## What is published

From `lib/python`, the module `open_bookmarks.py` and this
README, as described in pyproject.toml. The package has no
external dependencies. The import name after installation stays
`open_bookmarks`:

```python
from open_bookmarks import load_pack, validate_pack, flatten_urls
```

## Build and upload, manual step

Build from `lib/python`:

```sh
cd lib/python
python3 -m pip install --upgrade build twine
python3 -m build
python3 -m twine check dist/*
```

Check the built files first, without uploading:

```sh
python3 -m twine check dist/*
ls dist/
```

Upload to TestPyPI first, if you want a dry run against a real
index:

```sh
python3 -m twine upload --repository testpypi dist/*
```

Then upload to PyPI, as a separate manual step:

```sh
python3 -m twine upload dist/*
```

Use an API token for twine, not a password, and do not store the
token in the repo. After a successful upload, check the package
page on PyPI, and update the README install section to remove
the "not yet published" note. Do not upload a version that is
already on PyPI, and do not upload from a branch other than main
unless you mean to publish a pre-release.

## Still needed before any publish

- A decision to publish, from the repo owner.
- A PyPI account with upload rights for the name
  "open-bookmarks", or a different name if that name is taken at
  upload time.
- A PyPI API token, used only at upload time.
- A check that the package version in pyproject.toml has not
  already been published.
