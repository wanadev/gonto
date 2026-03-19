import copy
from pathlib import Path
from collections.abc import Iterator

import yaml
import jsonschema

from .log import logger
from .helpers import dict_merge

_CONFIG_FILES = [
    "gonto.yaml",
    "gonto.yml",
    ".gonto.yaml",
    ".gonto.yml",
]

_CONFIG_DIRS = [
    Path(__file__).parent.parent,  # Gonto install dir (Nuitka build)
    Path("~").expanduser(),  # User's home dir
    Path(".").absolute(),  # Current dir (project dir)
]

logger.debug("Searching configs from: %s" % str(_CONFIG_DIRS))

#: Default configuration
DEFAULT_CONFIG = {
    "gonto": {
        "cache_dir": None,
        "repository": None,
    },
    "targets": {},
}

#: JSON schema to validate the config
CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "gonto": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "cache_dir": {
                    "type": "string",
                },
                "repository": {
                    "type": "string",
                },
            },
            "required": ["cache_dir", "repository"],
        },
        "targets": {
            "type": "object",
            "additionalProperties": False,
            "patternProperties": {
                "^[a-zA-Z]+([a-zA-Z0-9_-]*[a-zA-Z0-9]+)?$": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "requires": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "name": {
                                        "type": "string",
                                    },
                                    "version": {
                                        "type": "string",
                                    },
                                    "platform": {
                                        "type": "string",
                                        "enum": ["win64", "win32", "multi"],
                                        "default": "win64",
                                    },
                                    "format": {
                                        "type": "string",
                                        "enum": ["vhd", "vhdx"],
                                        "default": "vhd",
                                    },
                                    "mount_point": {
                                        "type": "string",
                                        "pattern": r"^(|[D-Z]:\\)$",
                                        "default": "",
                                    },
                                    "env": {
                                        "$ref": "#/$defs/env",
                                    },
                                    "reg": {
                                        "$ref": "#/$defs/reg",
                                    },
                                },
                                "required": ["name", "version"],
                            },
                        },
                        "env": {
                            "$ref": "#/$defs/env",
                        },
                        "before_script": {
                            "type": "string",
                        },
                        "script": {
                            "type": "string",
                        },
                        "after_script": {
                            "type": "string",
                        },
                    },
                    "required": ["script"],
                }
            },
        },
    },
    "required": ["gonto", "targets"],
    "$defs": {
        "env": {
            "type": "object",
            "additionalProperties": False,
            "patternProperties": {
                "^[a-zA-Z_]+[a-zA-Z0-9_]*$": {
                    "type": "string",
                }
            },
        },
        "reg": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "root": {
                        "type": "string",
                        "enum": [
                            "HKEY_CLASSES_ROOT",
                            "HKEY_CURRENT_CONFIG",
                            "HKEY_CURRENT_USER",
                            "HKEY_DYN_DATA",
                            "HKEY_LOCAL_MACHINE",
                            "HKEY_PERFORMANCE_DATA",
                            "HKEY_USERS",
                        ],
                    },
                    "path": {
                        "type": "string",
                        "default": "",
                    },
                    "name": {
                        "type": "string",
                    },
                    "type": {
                        "type": "string",
                        "enum": [
                            "REG_DWORD",
                            "REG_DWORD_LITTLE_ENDIAN",
                            "REG_DWORD_BIG_ENDIAN",
                            "REG_QWORD",
                            "REG_QWORD_LITTLE_ENDIAN",
                            "REG_SZ",
                            "REG_EXPAND_SZ",
                            "REG_MULTI_SZ",
                        ],
                        "default": "REG_SZ",
                    },
                    "data": {
                        # Validation of type in "if/then/else" below
                        # NOTE: if "type" is not defined, the "then" branch is
                        #       used for validation (default value is ignored).
                    },
                },
                "if": {
                    "properties": {
                        "type": {
                            "enum": [
                                "REG_SZ",
                                "REG_EXPAND_SZ",
                                "REG_MULTI_SZ",
                            ],
                        },
                    },
                },
                "then": {
                    "properties": {
                        "data": {
                            "type": "string",
                        },
                    },
                },
                "else": {
                    "properties": {
                        "data": {
                            "type": "integer",
                        },
                    },
                },
                "required": ["root", "name", "data"],
            },
        },
    },
}


def list_config_files() -> Iterator[Path]:
    """Lists available configuration files.

    :return: The paths of the configuration files.
    """
    for folder in _CONFIG_DIRS:
        for file_ in _CONFIG_FILES:
            config_file_path = folder / file_
            if config_file_path.is_file():
                yield config_file_path


def validate_config(config: dict) -> tuple[bool, str]:
    """Validate the given config against the schema.

    :param config: The configuration to validate.

    :returns: ``(True, "")`` if the config is valid,
        ``(False, "error message")`` else.
    """
    try:
        jsonschema.validate(instance=config, schema=CONFIG_SCHEMA)
    except jsonschema.exceptions.ValidationError as error:
        return False, "%s: %s" % (
            ".".join([str(p) for p in error.path]) if error.path else "(root)",
            error.message,
        )
    else:
        return True, ""


def read_config() -> dict:
    """Read and merge the config.

    :returns: The final config as plain Python objects.
    """
    config_file_paths = list(list_config_files())

    if config_file_paths:
        logger.info(
            "Reading config from [%s]"
            % ", ".join(['"%s"' % str(p) for p in config_file_paths])
        )
    else:
        logger.warning("No configuration files found!")

    config = copy.deepcopy(DEFAULT_CONFIG)

    for config_file_path in config_file_paths:
        with open(config_file_path, "rb") as config_file:
            dict_merge(config, yaml.load(config_file, Loader=yaml.SafeLoader) or {})

    return config
