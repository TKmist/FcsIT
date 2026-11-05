# FcsIT update manifest template

Copy `Update_manifest.json` to `src/res/JSON_files/Update_manifest.json` and
replace every placeholder before publishing an update.

The manifest is declarative. It cannot contain Python code, shell commands,
pip options, package URLs, or absolute paths. Copy targets may use one leading
`..` only to install a bundled file beside the `FcsIT` application directory.

Fields:

- `schema_version`: supported manifest schema, currently `1`.
- `migration_id`: unique lowercase identifier using letters, digits, `_`, or
  `-`.
- `message`: explanation displayed before requesting user consent.
- `python_packages`: packages installed into the Python environment currently
  running FcsIT. Each entry contains a pip `requirement` and its
  `import_name`.
- `copy_files`: bundled files copied for `linux`, `windows`, or `all`
  platforms. Sources must be below the FcsIT source root. Targets are limited
  to the FcsIT directory or its immediate installation parent. Set
  `executable` for Linux launchers and CLI tools.
- `remove_files`: obsolete files relative to the installed FcsIT source root.
  Files are removed only after every required package installs and imports
  successfully.
- `requires_restart`: whether FcsIT should request a restart after migration.

Keep at least one operation in `python_packages`, `copy_files`, or
`remove_files`. Unknown fields are rejected so that new operations require an
explicit reader update.
