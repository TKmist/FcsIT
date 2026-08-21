# Copyright (C) 2026 TKmist (https://github.com/TKmist)
#
# This file is part of the FcsIT repository.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.
"""Command adapters for the FcsIT Dear PyGui analysis modules."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Callable

from include.command_dispatcher import CommandError, CommandRegistry


ContextProvider = Callable[[], dict[str, Any]]


def _argument(
    value_type: str,
    *,
    required: bool = False,
    description: str,
    enum: list[Any] | None = None,
    default: Any = None,
    has_default: bool = False,
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Support internal argument processing without changing public API."""
    definition: dict[str, Any] = {
        "type": value_type,
        "required": required,
        "description": description,
    }
    if enum is not None:
        definition["enum"] = enum
    if has_default:
        definition["default"] = default
    if constraints:
        definition["constraints"] = constraints
    return definition


def STRING(**kwargs: Any) -> dict[str, Any]:
    """Create metadata for a string command argument."""
    return _argument("string", **kwargs)


def NUMBER(**kwargs: Any) -> dict[str, Any]:
    """Create metadata for a numeric command argument."""
    return _argument("number", **kwargs)


def INTEGER(**kwargs: Any) -> dict[str, Any]:
    """Create metadata for an integer command argument."""
    return _argument("integer", **kwargs)


def BOOLEAN(**kwargs: Any) -> dict[str, Any]:
    """Create metadata for a Boolean command argument."""
    return _argument("boolean", **kwargs)


_COMMAND_ARGUMENTS: dict[str, dict[str, dict[str, Any]]] = {
    "gui.select_method": {
        "name": STRING(required=True, description="Analysis module name.", enum=["fitting", "ptu_corr", "time_bin_corr"]),
    },
    "gui.set_settings_visible": {
        "visible": BOOLEAN(required=True, description="Whether the settings window is visible."),
    },
    "gui.set_theme": {
        "theme": STRING(required=True, description="Theme selected for the next application start.", enum=["dark", "light"]),
    },
    "gui.set_plot_export_formats": {
        "csv": BOOLEAN(description="Enable CSV plot export."),
        "pickle": BOOLEAN(description="Enable Pickle plot export."),
    },
    "fitting.load_directory": {
        "directory": STRING(required=True, description="Input directory, or direct .dat file path for MC data."),
        "data_type": STRING(required=True, description="Input correlation data layout.", enum=["bin", "2C", "3C", "MC"]),
        "filename": STRING(description="Legacy MC filename used with a directory path."),
    },
    "fitting.select_file": {"filename": STRING(required=True, description="Exact loaded filename.")},
    "fitting.set_model": {"model": STRING(required=True, description="Exact analytical model name returned by fitting.list_models.")},
    "fitting.set_parameter": {
        "name": STRING(required=True, description="Parameter declared by the active model."),
        "value": NUMBER(required=True, description="Parameter value."),
        "minimum": NUMBER(description="Lower fitting bound."),
        "maximum": NUMBER(description="Upper fitting bound."),
        "fixed": BOOLEAN(description="Whether the parameter is fixed during fitting."),
    },
    "fitting.set_options": {
        "weights": BOOLEAN(description="Enable fit weights when supported."),
        "tau_min": NUMBER(description="Minimum fitted lag time."),
        "tau_max": NUMBER(description="Maximum fitted lag time."),
    },
    "fitting.set_time_units": {"value": NUMBER(required=True, description="Positive source time-unit multiplier in seconds.", constraints={"exclusive_minimum": 0, "finite": True})},
    "fitting.set_correlation_units": {"value": NUMBER(required=True, description="Positive source G(tau) multiplier.", constraints={"exclusive_minimum": 0, "finite": True})},
    "fitting.mark_result_for_removal": {
        "row": INTEGER(required=True, description="One-based stored-results row.", constraints={"minimum": 1}),
        "selected": BOOLEAN(required=True, description="Removal checkbox state."),
    },
    "fitting.remove_result": {"filename": STRING(required=True, description="Exact source filename whose stored rows will be removed.")},
    "fitting.export_results": {"path": STRING(required=True, description="Output file path.", constraints={"extensions": [".csv", ".dat", ".pickle"], "parent_must_exist": True})},
    "fitting.plot_all": {"directory": STRING(required=True, description="Existing output directory.", constraints={"must_exist": True})},
    "ptu_corr.load_directory": {"directory": STRING(required=True, description="Directory containing PTU or PT3 files.", constraints={"must_exist": True})},
    "ptu_corr.select_file": {"filename": STRING(required=True, description="Exact loaded PTU or PT3 filename.")},
    "ptu_corr.set_parameters": {
        "time_bin": NUMBER(description="Time-bin width."),
        "points": INTEGER(description="Number of correlation points."),
        "chunks": INTEGER(description="Number of signal chunks."),
        "tau_min": NUMBER(description="Minimum correlation lag time."),
        "tau_max": NUMBER(description="Maximum correlation lag time."),
        "cross_correlation": BOOLEAN(description="Enable cross-correlation."),
        "time_gate": BOOLEAN(description="Enable TCSPC time gating."),
        "background_correction": BOOLEAN(description="Enable TCSPC background correction."),
    },
    "ptu_corr.set_filtering": {
        "time_gate": BOOLEAN(description="Enable TCSPC time gating."),
        "background_correction": BOOLEAN(description="Enable background correction."),
        "gate_channel_1": _argument("array", description="Channel 1 [lower, upper] gate in ns.", constraints={"length": 2, "lower_less_than_upper": True}),
        "gate_channel_2": _argument("array", description="Channel 2 [lower, upper] gate in ns.", constraints={"length": 2, "lower_less_than_upper": True}),
        "background_channel_1": NUMBER(description="Channel 1 background level."),
        "background_channel_2": NUMBER(description="Channel 2 background level."),
    },
    "ptu_corr.set_custom_chunks": {"positions": _argument("array", required=True, description="Ordered non-overlapping {start, stop} ranges in seconds.", constraints={"min_items": 1, "start_minimum": 0, "start_less_than_stop": True, "non_overlapping": True})},
    "ptu_corr.select_tab": {"tab": STRING(required=True, description="Visible PTU analysis tab.", enum=["tcspc", "correlation"])},
    "ptu_corr.export_current": {
        "directory": STRING(required=True, description="Output directory; its final component may be created."),
        "format": STRING(required=True, description="Correlation output format.", enum=["corr", "dat"]),
    },
    "ptu_corr.export_all": {
        "directory": STRING(required=True, description="Output directory; its final component may be created."),
        "format": STRING(required=True, description="Correlation output format.", enum=["corr", "dat"]),
    },
    "time_bin_corr.load_directory": {
        "directory": STRING(required=True, description="Directory containing time-binned inputs.", constraints={"must_exist": True}),
        "output_directory": STRING(description="Existing output directory.", has_default=True, default="input directory"),
    },
    "time_bin_corr.select_file": {"filename": STRING(required=True, description="Exact loaded measurement filename.")},
    "time_bin_corr.set_parameters": {
        "time_bin": NUMBER(description="Time-bin width."),
        "points": INTEGER(description="Number of correlation points."),
        "chunks": INTEGER(description="Number of signal chunks."),
        "tau_min": NUMBER(description="Minimum correlation lag time."),
        "tau_max": NUMBER(description="Maximum correlation lag time."),
        "cross_correlation": BOOLEAN(description="Enable cross-correlation when available."),
    },
    "time_bin_corr.set_custom_chunks": {"positions": _argument("array", required=True, description="Ordered non-overlapping {start, stop} ranges in seconds.", constraints={"min_items": 1, "start_minimum": 0, "start_less_than_stop": True, "non_overlapping": True})},
}


_COMMAND_DESCRIPTIONS = {
    "gui.select_method": "Select an FcsIT analysis module.",
    "gui.set_settings_visible": "Show or hide the application settings window.",
    "gui.set_theme": "Select the theme persisted for the next application start.",
    "gui.set_plot_export_formats": "Set CSV and Pickle plot-export options.",
    "gui.save_settings": "Save current application settings as defaults.",
    "fitting.load_directory": "Load correlation data into the fitting module.",
    "fitting.select_file": "Select one loaded correlation curve.",
    "fitting.list_models": "List available analytical fitting models.",
    "fitting.set_model": "Select an analytical fitting model.",
    "fitting.set_parameter": "Set a model parameter, bounds, and fixed state.",
    "fitting.get_parameter_controls": "Read controls for every active model parameter.",
    "fitting.fit_current": "Fit the selected correlation curve.",
    "fitting.fit_all": "Fit all loaded correlation curves.",
    "fitting.set_options": "Set weighting and fitted lag-time range.",
    "fitting.reset_tau_range": "Reset the fitted lag-time range.",
    "fitting.set_time_units": "Set the source lag-time unit multiplier.",
    "fitting.set_correlation_units": "Set the source correlation-value multiplier.",
    "fitting.get_diagnostics": "Read fit statistics and residual diagnostics.",
    "fitting.keep_current": "Add the current fit to the results table.",
    "fitting.show_results": "Show the stored fitting-results table.",
    "fitting.close_results": "Close the fitting-results window.",
    "fitting.mark_result_for_removal": "Set a stored row's removal checkbox.",
    "fitting.remove_marked_results": "Remove every marked results row.",
    "fitting.remove_result": "Remove stored results for one source file.",
    "fitting.reset_workspace": "Clear per-file settings and stored results.",
    "fitting.reset_results": "Clear results while preserving per-file settings.",
    "fitting.export_results": "Export stored fitting results.",
    "fitting.plot_all": "Export plots for all stored fits.",
    "fitting.get_results": "Read current and stored fitting results.",
    "ptu_corr.load_directory": "Load PTU measurements.",
    "ptu_corr.select_file": "Select one loaded PTU measurement.",
    "ptu_corr.forget_current_measurement": "Forget the selected PTU session.",
    "ptu_corr.forget_all_measurements": "Forget all loaded PTU sessions.",
    "ptu_corr.set_parameters": "Set PTU correlation and filtering parameters.",
    "ptu_corr.set_filtering": "Set TCSPC gates and background levels.",
    "ptu_corr.set_custom_chunks": "Set custom PTU time-trace chunks.",
    "ptu_corr.select_tab": "Select the visible PTU tab.",
    "ptu_corr.calculate_filters_current": "Calculate filters for the selected PTU or PT3 file.",
    "ptu_corr.calculate_filters_all": "Calculate filters for all loaded PTU and PT3 files.",
    "ptu_corr.correlate_current": "Correlate the selected PTU or PT3 file.",
    "ptu_corr.correlate_all": "Correlate all loaded PTU and PT3 files.",
    "ptu_corr.export_current": "Export correlations for the selected PTU or PT3 file.",
    "ptu_corr.export_all": "Export correlations for all loaded PTU and PT3 files.",
    "ptu_corr.get_state": "Read PTU module state.",
    "time_bin_corr.load_directory": "Load time-binned measurements and output path.",
    "time_bin_corr.select_file": "Select one time-binned measurement.",
    "time_bin_corr.forget_current_measurement": "Forget the selected time-binned session and outputs.",
    "time_bin_corr.forget_all_measurements": "Forget all time-binned sessions and outputs.",
    "time_bin_corr.set_parameters": "Set time-binned correlation parameters.",
    "time_bin_corr.set_custom_chunks": "Set custom time-binned signal chunks.",
    "time_bin_corr.correlate_current": "Correlate the selected time-binned measurement.",
    "time_bin_corr.correlate_all": "Correlate all time-binned measurements.",
    "time_bin_corr.get_state": "Read time-binned correlation state.",
}


_READ_ONLY_COMMANDS = {
    "fitting.list_models", "fitting.get_parameter_controls",
    "fitting.get_diagnostics", "fitting.get_results",
    "ptu_corr.get_state", "time_bin_corr.get_state",
}
_DESTRUCTIVE_COMMANDS = {
    "fitting.remove_marked_results", "fitting.remove_result",
    "fitting.reset_workspace", "fitting.reset_results",
    "ptu_corr.forget_current_measurement", "ptu_corr.forget_all_measurements",
    "time_bin_corr.forget_current_measurement",
    "time_bin_corr.forget_all_measurements",
}
_LONG_RUNNING_COMMANDS = {
    "fitting.fit_current", "fitting.fit_all", "fitting.plot_all",
    "ptu_corr.calculate_filters_current", "ptu_corr.calculate_filters_all",
    "ptu_corr.correlate_current", "ptu_corr.correlate_all",
    "ptu_corr.export_current", "ptu_corr.export_all",
    "time_bin_corr.correlate_current", "time_bin_corr.correlate_all",
}


def _command_metadata(name: str) -> dict[str, Any]:
    """Support internal command metadata processing without changing public API."""
    return {
        "description": _COMMAND_DESCRIPTIONS[name],
        "arguments": _COMMAND_ARGUMENTS.get(name, {}),
        "returns": {
            "type": "object",
            "description": f"Structured result returned by {name}.",
        },
        "modifies_state": name not in _READ_ONLY_COMMANDS,
        "destructive": name in _DESTRUCTIVE_COMMANDS,
        "long_running": name in _LONG_RUNNING_COMMANDS,
    }


class FcsITGuiCommands:
    """Expose existing GUI callbacks through validated command handlers."""

    METHOD_PATHS = {
        "fitting": "Methods/FCS_fitting",
        "ptu_corr": "Methods/PTU_Corr",
        "time_bin_corr": "Methods/TIME_BIN_Corr",
    }

    def __init__(self, dpg: Any, context_provider: ContextProvider) -> None:
        """Initialize FcsITGuiCommands for its documented use."""
        self.dpg = dpg
        self.context_provider = context_provider

    def register_all(self, registry: CommandRegistry) -> None:
        """Execute register all and return the documented result."""
        commands = {
            "gui.select_method": self.select_method,
            "gui.set_settings_visible": self.set_settings_visible,
            "gui.set_theme": self.set_theme,
            "gui.set_plot_export_formats": self.set_plot_export_formats,
            "gui.save_settings": self.save_settings,
            "fitting.load_directory": self.fitting_load_directory,
            "fitting.select_file": self.fitting_select_file,
            "fitting.list_models": self.fitting_list_models,
            "fitting.set_model": self.fitting_set_model,
            "fitting.set_parameter": self.fitting_set_parameter,
            "fitting.get_parameter_controls": self.fitting_get_parameter_controls,
            "fitting.fit_current": self.fitting_fit_current,
            "fitting.fit_all": self.fitting_fit_all,
            "fitting.set_options": self.fitting_set_options,
            "fitting.reset_tau_range": self.fitting_reset_tau_range,
            "fitting.set_time_units": self.fitting_set_time_units,
            "fitting.set_correlation_units": self.fitting_set_correlation_units,
            "fitting.get_diagnostics": self.fitting_get_diagnostics,
            "fitting.keep_current": self.fitting_keep_current,
            "fitting.show_results": self.fitting_show_results,
            "fitting.close_results": self.fitting_close_results,
            "fitting.mark_result_for_removal": (
                self.fitting_mark_result_for_removal
            ),
            "fitting.remove_marked_results": self.fitting_remove_marked_results,
            "fitting.remove_result": self.fitting_remove_result,
            "fitting.reset_workspace": self.fitting_reset_workspace,
            "fitting.reset_results": self.fitting_reset_results,
            "fitting.export_results": self.fitting_export_results,
            "fitting.plot_all": self.fitting_plot_all,
            "fitting.get_results": self.fitting_get_results,
            "ptu_corr.load_directory": self.ptu_load_directory,
            "ptu_corr.select_file": self.ptu_select_file,
            "ptu_corr.forget_current_measurement": (
                self.ptu_forget_current_measurement
            ),
            "ptu_corr.forget_all_measurements": self.ptu_forget_all_measurements,
            "ptu_corr.set_parameters": self.ptu_set_parameters,
            "ptu_corr.set_filtering": self.ptu_set_filtering,
            "ptu_corr.set_custom_chunks": self.ptu_set_custom_chunks,
            "ptu_corr.select_tab": self.ptu_select_tab,
            "ptu_corr.calculate_filters_current": self.ptu_filters_current,
            "ptu_corr.calculate_filters_all": self.ptu_filters_all,
            "ptu_corr.correlate_current": self.ptu_correlate_current,
            "ptu_corr.correlate_all": self.ptu_correlate_all,
            "ptu_corr.export_current": self.ptu_export_current,
            "ptu_corr.export_all": self.ptu_export_all,
            "ptu_corr.get_state": self.ptu_get_state,
            "time_bin_corr.load_directory": self.time_bin_load_directory,
            "time_bin_corr.select_file": self.time_bin_select_file,
            "time_bin_corr.forget_current_measurement": (
                self.time_bin_forget_current_measurement
            ),
            "time_bin_corr.forget_all_measurements": (
                self.time_bin_forget_all_measurements
            ),
            "time_bin_corr.set_parameters": self.time_bin_set_parameters,
            "time_bin_corr.set_custom_chunks": (
                self.time_bin_set_custom_chunks
            ),
            "time_bin_corr.correlate_current": self.time_bin_correlate_current,
            "time_bin_corr.correlate_all": self.time_bin_correlate_all,
            "time_bin_corr.get_state": self.time_bin_get_state,
        }
        for name, handler in commands.items():
            registry.register(name, handler, _command_metadata(name))

    def set_settings_visible(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Show or hide the application settings window through its callbacks."""
        (visible,) = self._require_arguments(arguments, "visible")
        settings = self._context().get("settwin")
        if settings is None:
            raise CommandError("The settings window has not initialized.")
        if bool(visible):
            settings.show_set_win()
        else:
            settings.hide_set_win()
        return {
            "visible": bool(self.dpg.is_item_shown("Settings_window")),
        }

    def set_theme(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Set the settings-list theme selection without applying or saving it."""
        (theme,) = self._require_arguments(arguments, "theme")
        if theme not in {"dark", "light"}:
            raise CommandError("Theme must be one of: dark, light.")
        self.dpg.set_value("theme_choose", theme)
        return {
            "theme": self.dpg.get_value("theme_choose"),
            "applied": False,
            "saved": False,
        }

    def set_plot_export_formats(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Set plot export formats without applying or saving defaults."""
        tags = {
            "csv": "Sett_export_plot_as_csv",
            "pickle": "Sett_export_plot_as_pickle",
        }
        if not arguments:
            raise CommandError("At least one plot export format is required.")
        self._set_known_values(arguments, tags)
        self.dpg.configure_item("Setts_save_defaults", enabled=True)
        return {
            **self._read_values(tags),
            "saved": False,
        }

    def save_settings(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Save current settings using the GUI's Save as defaults callback."""
        if arguments:
            raise CommandError("This command does not accept arguments.")
        settings = self._context().get("settwin")
        if settings is None:
            raise CommandError("The settings window has not initialized.")
        settings.callback_save_as_def("Setts_save_defaults", None)
        return {
            "saved": True,
            "visible": bool(self.dpg.is_item_shown("Settings_window")),
            "csv": bool(self.dpg.get_value("Sett_export_plot_as_csv")),
            "pickle": bool(
                self.dpg.get_value("Sett_export_plot_as_pickle")
            ),
        }

    def _context(self) -> dict[str, Any]:
        """Support internal context processing without changing public API."""
        return self.context_provider()

    def _require_arguments(
        self, arguments: dict[str, Any], *names: str
    ) -> list[Any]:
        """Support internal require arguments processing without changing public API."""
        missing = [name for name in names if name not in arguments]
        if missing:
            raise CommandError(f"Missing arguments: {', '.join(missing)}")
        return [arguments[name] for name in names]

    def _directory(self, value: Any) -> Path:
        """Support internal directory processing without changing public API."""
        path = Path(str(value)).expanduser().resolve()
        if not path.is_dir():
            raise CommandError(f"Directory does not exist: {path}")
        return path

    def _export_directory(self, value: Any) -> Path:
        """Resolve an export directory and create only its final component."""
        path = Path(str(value)).expanduser().resolve()
        if path.exists():
            if not path.is_dir():
                raise CommandError(f"Export path is not a directory: {path}")
            return path
        if not path.parent.is_dir():
            raise CommandError(
                f"Export directory parent does not exist: {path.parent}"
            )
        try:
            path.mkdir()
        except OSError as exc:
            raise CommandError(
                f"Could not create export directory: {path}: {exc}"
            ) from exc
        return path

    def _method(self, name: str) -> Any:
        """Support internal method processing without changing public API."""
        context = self._context()
        mounted = context["inV"].mounted_method
        expected = self.METHOD_PATHS[name]
        if mounted != expected:
            raise CommandError(
                f"Method '{name}' is not active. Call gui.select_method first."
            )
        method = context.get("method_cmn")
        if method is None:
            raise CommandError("The active method has not initialized its GUI state.")
        return method

    def select_method(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute select method and return the documented result."""
        (name,) = self._require_arguments(arguments, "name")
        if name not in self.METHOD_PATHS:
            raise CommandError(
                f"Unsupported method: {name}. Expected one of "
                f"{', '.join(sorted(self.METHOD_PATHS))}."
            )
        context = self._context()
        if context["inV"].mounted_method != self.METHOD_PATHS[name]:
            callbacks = {
                "fitting": context["fcs_manu_F"].callback_FCS_FITTING_menu,
                "ptu_corr": context["PTU_Corr_manu_F"].callback_PTU_Corr_menu,
                "time_bin_corr": context["TB_corr_manu_F"].callback_TB_corr_menu,
            }
            callbacks[name]()
        return {"active_method": name}

    def fitting_load_directory(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute fitting load directory and return the documented result."""
        directory, data_type = self._require_arguments(
            arguments, "directory", "data_type"
        )
        if data_type not in {"bin", "2C", "3C", "MC"}:
            raise CommandError("data_type must be one of: bin, 2C, 3C, MC")
        method = self._method("fitting")
        method.FCS_data_type = data_type
        if data_type == "MC":
            requested_path = Path(str(directory)).expanduser().resolve()
            if requested_path.is_file():
                source = requested_path
                path = source.parent
            else:
                path = self._directory(directory)
                candidates = sorted(path.glob("*.dat"))
                requested = arguments.get("filename")
                source = path / requested if requested else None
                if source is None and len(candidates) == 1:
                    source = candidates[0]
            if source is not None and source.suffix.lower() != ".dat":
                raise CommandError("MC data source must be a .dat file.")
            if source is None or not source.is_file():
                raise CommandError(
                    "MC data require a path to a .dat file. The legacy "
                    "directory plus filename form is also accepted."
                )
            method.callback_directory_select(
                None,
                {
                    "file_path_name": str(source),
                    "file_name": source.name,
                    "current_path": str(path),
                },
            )
        else:
            path = self._directory(directory)
            method.callback_directory_select(None, {"file_path_name": str(path)})
        return {
            "directory": str(path),
            "source_file": str(source) if data_type == "MC" else None,
            "data_type": data_type,
            "files": list(method.files),
            "selected_file": getattr(method, "anal_file", None),
        }

    def fitting_select_file(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute fitting select file and return the documented result."""
        (filename,) = self._require_arguments(arguments, "filename")
        method = self._method("fitting")
        if filename not in method.files:
            raise CommandError(f"File is not loaded: {filename}")
        self.dpg.set_value("file_box", filename)
        method.callback_listbox("file_box", filename)
        return {"selected_file": filename}

    def fitting_list_models(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute fitting list models and return the documented result."""
        method = self._method("fitting")
        return {
            "models": list(method.Models),
            "selected_model": self.dpg.get_value("model_choose"),
        }

    def fitting_set_model(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute fitting set model and return the documented result."""
        (model,) = self._require_arguments(arguments, "model")
        method = self._method("fitting")
        if model not in method.Models:
            raise CommandError(f"Unknown fitting model: {model}")
        self.dpg.set_value("model_choose", model)
        method.callback_models("model_choose", model)
        return {"model": model, "parameters": list(method.VARIABLES)}

    def fitting_set_parameter(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute fitting set parameter and return the documented result."""
        name, value = self._require_arguments(arguments, "name", "value")
        method = self._method("fitting")
        if name not in method.VARIABLES:
            raise CommandError(f"Unknown model parameter: {name}")
        arguments = dict(arguments)
        value = float(value)
        if str(name).startswith("tau_d"):
            tau_max = float(self.dpg.get_value("df_max"))
            maximum = float(arguments.get("maximum", tau_max))
            minimum = float(arguments.get("minimum", 0.0))
            if maximum > tau_max:
                raise CommandError(
                    f"{name} maximum ({maximum}) cannot exceed tau_max ({tau_max})."
                )
            if value > tau_max:
                raise CommandError(
                    f"{name} value ({value}) cannot exceed tau_max ({tau_max})."
                )
            if minimum > maximum:
                raise CommandError(f"{name} minimum cannot exceed its maximum.")
            arguments["maximum"] = maximum
        slider = f"VARIABLES_{name}_slider"
        self.dpg.set_value(slider, value)
        method.callback_slider(slider, value)
        if "minimum" in arguments:
            tag = f"VARIABLES_{name}_min"
            self.dpg.set_value(tag, arguments["minimum"])
            method.callback_range_min(tag, arguments["minimum"])
        if "maximum" in arguments:
            tag = f"VARIABLES_{name}_max"
            self.dpg.set_value(tag, arguments["maximum"])
            method.callback_range_max(tag, arguments["maximum"])
        if "fixed" in arguments:
            self.dpg.set_value(f"VARIABLES_{name}_check", bool(arguments["fixed"]))
        return {
            "name": name,
            "value": self.dpg.get_value(slider),
            "fixed": self.dpg.get_value(f"VARIABLES_{name}_check"),
            "minimum": self.dpg.get_value(f"VARIABLES_{name}_min"),
            "maximum": self.dpg.get_value(f"VARIABLES_{name}_max"),
        }

    def fitting_get_parameter_controls(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Map controls for every parameter declared by the active model."""
        method = self._method("fitting")
        controls = []
        for name in method.VARIABLES:
            tags = {
                "value": f"VARIABLES_{name}_slider",
                "minimum": f"VARIABLES_{name}_min",
                "maximum": f"VARIABLES_{name}_max",
                "fixed": f"VARIABLES_{name}_check",
            }
            missing = [
                role for role, tag in tags.items()
                if not self.dpg.does_item_exist(tag)
            ]
            if missing:
                raise CommandError(
                    f"Parameter {name} is missing controls: {', '.join(missing)}"
                )
            controls.append(
                {
                    "name": name,
                    "value": float(self.dpg.get_value(tags["value"])),
                    "minimum": float(self.dpg.get_value(tags["minimum"])),
                    "maximum": float(self.dpg.get_value(tags["maximum"])),
                    "fixed": bool(self.dpg.get_value(tags["fixed"])),
                    "widgets": tags,
                }
            )
        return {
            "model": self.dpg.get_value("model_choose"),
            "controls": controls,
        }

    def fitting_fit_current(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute fitting fit current and return the documented result."""
        method = self._method("fitting")
        method.callback_fit_button("Fit_button", None)
        return self.fitting_get_results({})

    def fitting_fit_all(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute fitting fit all and return the documented result."""
        method = self._method("fitting")
        method.callback_fit_all_button("Fit_all_button", None)
        return self.fitting_get_results({})

    def fitting_set_options(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute fitting set options and return the documented result."""
        method = self._method("fitting")
        if "weights" in arguments:
            use_weights = bool(arguments["weights"])
            if method.FCS_data_type == "2C" and use_weights:
                raise CommandError("Weights are unavailable for two-column data.")
            self.dpg.set_value("FITing_checkbox", use_weights)
        if "tau_min" in arguments:
            value = float(arguments["tau_min"])
            self.dpg.set_value("df_min", value)
            method.callback_df_range("df_min", value)
        if "tau_max" in arguments:
            value = float(arguments["tau_max"])
            self.dpg.set_value("df_max", value)
            method.callback_df_range("df_max", value)
        return {
            "weights": bool(self.dpg.get_value("FITing_checkbox")),
            "tau_min": float(self.dpg.get_value("df_min")),
            "tau_max": float(self.dpg.get_value("df_max")),
            "data_type": method.FCS_data_type,
        }

    def fitting_reset_tau_range(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Restore the fitted lag-time range to the complete loaded curve."""
        method = self._method("fitting")
        method.callback_reset_df_range("Reset_range", None)
        return {
            "tau_min": float(self.dpg.get_value("df_min")),
            "tau_max": float(self.dpg.get_value("df_max")),
        }

    def fitting_set_time_units(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Set the source lag-time unit multiplier in seconds."""
        (value,) = self._require_arguments(arguments, "value")
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise CommandError("Time units must be a positive finite number.")
        method = self._method("fitting")
        self.dpg.set_value("Xunits", value)
        method.callback_Xunits("Xunits", value)
        return {
            "time_units": float(self.dpg.get_value("Xunits")),
            "tau_min": float(self.dpg.get_value("df_min")),
            "tau_max": float(self.dpg.get_value("df_max")),
        }

    def fitting_set_correlation_units(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Set the source G(tau) value multiplier."""
        (value,) = self._require_arguments(arguments, "value")
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise CommandError(
                "Correlation units must be a positive finite number."
            )
        method = self._method("fitting")
        self.dpg.set_value("Yunits", value)
        method.callback_Xunits("Yunits", value)
        return {
            "correlation_units": float(self.dpg.get_value("Yunits")),
        }

    def fitting_get_diagnostics(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute fitting get diagnostics and return the documented result."""
        method = self._method("fitting")
        if not getattr(method, "res_dict", None):
            raise CommandError("Fit the selected curve before reading diagnostics.")
        frame = method.df
        prediction = method.my_universal_function(
            frame.X.values, **method.res_dict
        )
        residuals = frame.Y.values - prediction
        weighted = bool(self.dpg.get_value("FITing_checkbox"))
        if weighted and "Y_err" in frame.columns:
            residuals = residuals / frame.Y_err.values
        count = len(residuals)
        mean = float(sum(residuals) / count)
        rms = float((sum(float(v) ** 2 for v in residuals) / count) ** 0.5)
        errors = dict(getattr(method, "err_messages", {}))
        return {
            **self.fitting_get_results({}),
            "residuals": {
                "count": count,
                "mean": mean,
                "rms": rms,
                "maximum_absolute": float(max(abs(v) for v in residuals)),
                "weighted": weighted,
            },
            "fit_error": getattr(method, "anal_file", None) in errors,
            "error_files": list(errors),
        }

    def fitting_keep_current(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute fitting keep current and return the documented result."""
        method = self._method("fitting")
        method.callback_keep_res_button("keep_results_butt", None)
        return self.fitting_get_results({})

    def fitting_show_results(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Show the stored fitting-results table without modifying it."""
        method = self._method("fitting")
        if method.RES_DF.empty:
            raise CommandError("There are no stored fitting results to show.")
        method.callback_show_res_button("show_results_butt", None)
        return {
            "visible": bool(self.dpg.is_item_shown("show_res_win")),
            "stored_results": method.RES_DF.to_dict(orient="records"),
        }

    def fitting_close_results(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Close the stored fitting-results window without modifying data."""
        self._method("fitting")
        self.dpg.configure_item("show_res_win", show=False)
        return {"visible": bool(self.dpg.is_item_shown("show_res_win"))}

    def fitting_mark_result_for_removal(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Set the removal checkbox for a one-based results-table row."""
        row, selected = self._require_arguments(arguments, "row", "selected")
        row = int(row)
        method = self._method("fitting")
        if row < 1 or row > len(method.RES_DF):
            raise CommandError(
                f"Result row must be between 1 and {len(method.RES_DF)}."
            )
        tag = f"results_delete_{row - 1}_check"
        if not self.dpg.does_item_exist(tag):
            raise CommandError(f"Removal checkbox is unavailable for row {row}.")
        self.dpg.set_value(tag, bool(selected))
        return {"row": row, "selected": bool(self.dpg.get_value(tag))}

    def fitting_remove_marked_results(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Invoke the GUI Remove action for checked result rows."""
        method = self._method("fitting")
        marked = [
            index + 1
            for index in method.RES_DF.index
            if self.dpg.get_value(f"results_delete_{index}_check")
        ]
        if not marked:
            raise CommandError("No result rows are marked for removal.")
        method.callback_remove_result_button("remove_button_results", None)
        return {
            "removed_rows": marked,
            "stored_results": method.RES_DF.to_dict(orient="records"),
        }

    def fitting_remove_result(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute fitting remove result and return the documented result."""
        (filename,) = self._require_arguments(arguments, "filename")
        method = self._method("fitting")
        stored = method.RES_DF
        method.RES_DF = stored.loc[stored["file"] != filename].reset_index(drop=True)
        method.workspace_iso["STORED RESULTS"] = {
            column: list(method.RES_DF[column].values)
            for column in method.RES_DF.columns
        }
        method.write_res_to_table()
        method.write_to_average_table()
        return self.fitting_get_results({})

    def fitting_reset_workspace(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute fitting reset workspace and return the documented result."""
        method = self._method("fitting")
        method.callback_reset_workspace("reset_workspace_menu_item", None)
        return self.fitting_get_results({})

    def fitting_reset_results(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute fitting reset results and return the documented result."""
        method = self._method("fitting")
        method.callback_reset_workspace_results(
            "reset_workspace_results_menu_item", None
        )
        return self.fitting_get_results({})

    def fitting_export_results(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute fitting export results and return the documented result."""
        (path_value,) = self._require_arguments(arguments, "path")
        path = Path(str(path_value)).expanduser().resolve()
        if not path.parent.is_dir():
            raise CommandError(f"Output directory does not exist: {path.parent}")
        extension = path.suffix.lower()
        if extension not in {".csv", ".dat", ".pickle"}:
            raise CommandError("Result format must be csv, dat, or pickle.")
        method = self._method("fitting")
        method.callback_directory_export(
            None,
            {
                "file_path_name": str(path),
                "file_name": path.name,
                "current_filter": extension,
            },
        )
        return {"path": str(path), "rows": len(method.RES_DF)}

    def fitting_plot_all(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute fitting plot all and return the documented result."""
        (directory,) = self._require_arguments(arguments, "directory")
        output = self._directory(directory)
        method = self._method("fitting")
        self.dpg.set_value("Sett_export_plot_as_png", True)
        method.callback_plot_all_to_files(
            None, {"file_path_name": str(output)}
        )
        paths = sorted(str(path) for path in output.glob("*.png"))
        return {"directory": str(output), "plots": paths}

    def fitting_get_results(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute fitting get results and return the documented result."""
        method = self._method("fitting")
        stored = getattr(method, "RES_DF", None)
        return {
            "selected_file": getattr(method, "anal_file", None),
            "parameters": getattr(method, "res_dict", {}),
            "parameter_errors": getattr(method, "reserr_dict", {}),
            "chi_square": getattr(method, "chisqr", None),
            "reduced_chi_square": getattr(method, "redchi", None),
            "p_value": getattr(method, "pvalue", None),
            "error_files": list(getattr(method, "err_messages", {})),
            "stored_results": (
                stored.to_dict(orient="records") if stored is not None else []
            ),
        }

    def ptu_load_directory(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute ptu load directory and return the documented result."""
        (directory,) = self._require_arguments(arguments, "directory")
        method = self._method("ptu_corr")
        path = self._directory(directory)
        method.callback_directory_select(None, {"current_path": str(path)})
        return self.ptu_get_state({})

    def ptu_select_file(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute ptu select file and return the documented result."""
        (filename,) = self._require_arguments(arguments, "filename")
        method = self._method("ptu_corr")
        if filename not in method.files:
            raise CommandError(f"File is not loaded: {filename}")
        self.dpg.set_value("file_box", filename)
        method.callback_listbox("file_box", filename)
        return self.ptu_get_state({})

    def ptu_forget_all_measurements(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute ptu forget all measurements and return the documented result."""
        method = self._method("ptu_corr")
        method.callback_Forget_all_PTU_data()
        return self.ptu_get_state({})

    def ptu_forget_current_measurement(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute ptu forget current measurement and return the documented result."""
        method = self._method("ptu_corr")
        method.callback_Forget_PTU_data()
        return self.ptu_get_state({})

    def ptu_set_parameters(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute ptu set parameters and return the documented result."""
        method = self._method("ptu_corr")
        tags = {
            "time_bin": "left_panel_drag_time_binning",
            "points": "left_panel_drag_subs",
            "chunks": "left_panel_N_chunks",
            "tau_min": "left_panel_tau_min",
            "tau_max": "left_panel_tau_max",
            "cross_correlation": "FCS_cross_check",
            "time_gate": "TCSPC_timegate_check",
            "background_correction": "TCSPC_BG_correction_check",
        }
        self._set_known_values(arguments, tags)
        if "time_bin" in arguments:
            method.callback_left_panel_drag_time_binning(
                tags["time_bin"], arguments["time_bin"]
            )
        elif "chunks" in arguments:
            method.on_chunks_released()
        if "time_gate" in arguments:
            method.callback_tcspc_timegate(
                tags["time_gate"], bool(arguments["time_gate"])
            )
        if "background_correction" in arguments:
            method.callback_tcspc_BG(
                tags["background_correction"],
                bool(arguments["background_correction"]),
            )
        if "cross_correlation" in arguments:
            method.callback_crossCorr_check(
                "DUMMY",
                bool(arguments["cross_correlation"]),
            )
        return self.ptu_get_state({})

    def ptu_set_filtering(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Set TCSPC gating draglines and background levels."""
        method = self._method("ptu_corr")
        self._activate_ptu_tab(method, "tcspc")
        if not arguments:
            raise CommandError("At least one filtering setting is required.")

        if "time_gate" in arguments:
            enabled = bool(arguments["time_gate"])
            self.dpg.set_value("TCSPC_timegate_check", enabled)
            method.callback_tcspc_timegate("TCSPC_timegate_check", enabled)
        if "background_correction" in arguments:
            enabled = bool(arguments["background_correction"])
            self.dpg.set_value("TCSPC_BG_correction_check", enabled)
            method.callback_tcspc_BG(
                "TCSPC_BG_correction_check", enabled
            )

        gate_tags = {
            "gate_channel_1": (
                "TCSPC_L_dline_ch1",
                "TCSPC_U_dline_ch1",
                1,
            ),
            "gate_channel_2": (
                "TCSPC_L_dline_ch2",
                "TCSPC_U_dline_ch2",
                2,
            ),
        }
        for name, (lower_tag, upper_tag, channel_number) in gate_tags.items():
            if name not in arguments:
                continue
            if channel_number > len(method.channels):
                raise CommandError(
                    f"{name} is unavailable for this measurement."
                )
            gate = arguments[name]
            if not isinstance(gate, (list, tuple)) or len(gate) != 2:
                raise CommandError(f"{name} must contain [lower, upper].")
            lower, upper = map(float, gate)
            if lower >= upper:
                raise CommandError(f"{name} lower value must be below upper.")
            method.TCSCP_draglines[lower_tag] = lower
            method.TCSCP_draglines[upper_tag] = upper
            self.dpg.set_value(lower_tag, lower)
            self.dpg.set_value(upper_tag, upper)
            method.callback_TCSPC_dragline(lower_tag, lower)
            method.callback_TCSPC_dragline(upper_tag, upper)

        background_tags = {
            "background_channel_1": ("TCSPC_BG_dline_ch1", 1),
            "background_channel_2": ("TCSPC_BG_dline_ch2", 2),
        }
        for name, (tag, channel_number) in background_tags.items():
            if name not in arguments:
                continue
            if channel_number > len(method.channels):
                raise CommandError(
                    f"{name} is unavailable for this measurement."
                )
            value = float(arguments[name])
            self.dpg.set_value(tag, value)
            if self.dpg.get_value("TCSPC_BG_correction_check"):
                method.subtract_tcspc(tag, value)

        method.META_data["TCSPC info"] = method.TCSPC_snapshot()
        return self.ptu_get_state({})

    def ptu_set_custom_chunks(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Set custom time-trace chunk boundaries for the selected file."""
        (positions,) = self._require_arguments(arguments, "positions")
        if not isinstance(positions, list) or not positions:
            raise CommandError("positions must be a non-empty array.")
        normalized = []
        previous_stop = None
        for index, position in enumerate(positions, start=1):
            if not isinstance(position, dict):
                raise CommandError("Each chunk position must be an object.")
            if "start" not in position or "stop" not in position:
                raise CommandError(
                    f"Chunk {index} requires start and stop values."
                )
            start = float(position["start"])
            stop = float(position["stop"])
            if start < 0 or start >= stop:
                raise CommandError(
                    f"Invalid boundaries for chunk {index}: {start}, {stop}."
                )
            if previous_stop is not None and start < previous_stop:
                raise CommandError("Custom chunks must not overlap.")
            normalized.append((start, stop))
            previous_stop = stop

        method = self._method("ptu_corr")
        maximum = float(method.TT_xdata_1[-1])
        if normalized[-1][1] > maximum:
            raise CommandError(
                f"Custom chunk stop exceeds measurement duration {maximum}."
            )

        self.dpg.set_value("Custom_chunks_check", True)
        self.dpg.set_value("left_panel_N_chunks", len(normalized))
        method.on_chunks_released()
        two_channels = len(method.channels) == 2
        for index, (start, stop) in enumerate(normalized, start=1):
            start_tag = f"Chunk_1_{index}_start_dragline"
            stop_tag = f"Chunk_1_{index}_stop_dragline"
            self.dpg.set_value(start_tag, start)
            self.dpg.set_value(stop_tag, stop)
            if two_channels:
                self.dpg.set_value(
                    f"Chunk_2_{index}_start_dragline", start
                )
                self.dpg.set_value(f"Chunk_2_{index}_stop_dragline", stop)

        for index, (start, stop) in enumerate(normalized, start=1):
            start_tag = f"Chunk_1_{index}_start_dragline"
            stop_tag = f"Chunk_1_{index}_stop_dragline"
            method.callback_chunk_drag_line(start_tag, start, None)
            method.callback_chunk_drag_line(stop_tag, stop, None)

        method.show_chunks_drag_lines(
            "Custom_chunks_check", True, allow_reset=False
        )
        method.call_back_update_TCSPC()
        method._after_chunks_changed()
        return self.ptu_get_state({})

    def _activate_ptu_tab(self, method: Any, tab: str) -> None:
        """Select the PTU tab before a long-running GUI action."""
        switchers = {
            "tcspc": method.switch_to_tcspc_tab,
            "correlation": method.switch_to_corr_tab,
        }
        switchers[tab]()

    def ptu_select_tab(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Select a visible PTU tab without starting an operation."""
        (tab,) = self._require_arguments(arguments, "tab")
        if tab not in {"tcspc", "correlation"}:
            raise CommandError("tab must be one of: tcspc, correlation")
        method = self._method("ptu_corr")
        self._activate_ptu_tab(method, tab)
        state = self.ptu_get_state({})
        state["active_tab"] = tab
        return state

    def ptu_filters_current(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute ptu filters current and return the documented result."""
        method = self._method("ptu_corr")
        self._activate_ptu_tab(method, "tcspc")
        method.callback_calc_fltr_one("Calculate_filter_once_button", None)
        return self.ptu_get_state({})

    def ptu_filters_all(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute ptu filters all and return the documented result."""
        method = self._method("ptu_corr")
        self._activate_ptu_tab(method, "tcspc")
        method.callback_calc_fltr_all("Calculate_filter_all_button", None)
        return self.ptu_get_state({})

    def ptu_correlate_current(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute ptu correlate current and return the documented result."""
        method = self._method("ptu_corr")
        self._activate_ptu_tab(method, "correlation")
        method.callback_calc_corr_one("Calculate_correlation_once_button", None)
        return self.ptu_get_state({})

    def ptu_correlate_all(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute ptu correlate all and return the documented result."""
        method = self._method("ptu_corr")
        self._activate_ptu_tab(method, "correlation")
        method.callback_calc_corr_all("Calculate_correlation_all_button", None)
        return self.ptu_get_state({})

    def ptu_export_all(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute ptu export all and return the documented result."""
        directory, file_format = self._require_arguments(
            arguments, "directory", "format"
        )
        if file_format not in {"corr", "dat"}:
            raise CommandError("format must be one of: corr, dat")
        method = self._method("ptu_corr")
        self._activate_ptu_tab(method, "correlation")
        path = self._export_directory(directory)
        missing = method.check_if_all_Correlations_exists()
        if missing:
            raise CommandError(
                "Correlation data is missing for: " + ", ".join(missing)
            )
        method.corr_export_all = "all"
        method.corr_export_ext = f".{file_format}"
        method.callback_export_correlation(None, {"current_path": str(path)})
        exported = sorted(
            str(item.relative_to(path))
            for item in path.glob(f"*/**/*.{file_format}")
            if item.is_file()
        )
        return {
            "directory": str(path),
            "format": file_format,
            "files": exported,
        }

    def ptu_export_current(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute ptu export current and return the documented result."""
        directory, file_format = self._require_arguments(
            arguments, "directory", "format"
        )
        if file_format not in {"corr", "dat"}:
            raise CommandError("format must be one of: corr, dat")
        method = self._method("ptu_corr")
        self._activate_ptu_tab(method, "correlation")
        if (
            len(method.META_data["FCS info"]["AutoCorr_1"]) == 0
            and len(method.META_data["FCS info"]["AutoCorr_2"]) == 0
        ):
            raise CommandError("The selected file has no correlation data.")
        path = self._export_directory(directory)
        method.corr_export_all = "single"
        method.corr_export_ext = f".{file_format}"
        method.callback_export_correlation(None, {"current_path": str(path)})
        output_name = Path(method.anal_file).with_suffix(
            f".{file_format}"
        ).name
        exported = sorted(
            str(item.relative_to(path))
            for item in path.glob(f"*/{output_name}")
            if item.is_file()
        )
        return {
            "directory": str(path),
            "format": file_format,
            "selected_file": method.anal_file,
            "files": exported,
        }

    def ptu_get_state(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute ptu get state and return the documented result."""
        method = self._method("ptu_corr")
        return {
            "directory": getattr(method, "last_directory", None),
            "files": list(getattr(method, "files", [])),
            "selected_file": getattr(method, "anal_file", None),
            "channels": list(getattr(method, "channels", [])),
            "parameters": self._read_values(
                {
                    "time_bin": "left_panel_drag_time_binning",
                    "points": "left_panel_drag_subs",
                    "chunks": "left_panel_N_chunks",
                    "tau_min": "left_panel_tau_min",
                    "tau_max": "left_panel_tau_max",
                    "cross_correlation": "FCS_cross_check",
                }
            ),
            "filtering": self._read_values(
                {
                    "time_gate": "TCSPC_timegate_check",
                    "background_correction": "TCSPC_BG_correction_check",
                    "gate_channel_1_lower": "TCSPC_L_dline_ch1",
                    "gate_channel_1_upper": "TCSPC_U_dline_ch1",
                    "gate_channel_2_lower": "TCSPC_L_dline_ch2",
                    "gate_channel_2_upper": "TCSPC_U_dline_ch2",
                    "background_channel_1": "TCSPC_BG_dline_ch1",
                    "background_channel_2": "TCSPC_BG_dline_ch2",
                }
            ),
            "custom_chunks": {
                "enabled": bool(self.dpg.get_value("Custom_chunks_check")),
                "positions": [
                    {
                        "start": chunk["values"][0],
                        "stop": chunk["values"][1],
                    }
                    for chunk in getattr(method, "chunks", {}).values()
                ],
            },
        }

    def time_bin_load_directory(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute time bin load directory and return the documented result."""
        (directory,) = self._require_arguments(arguments, "directory")
        method = self._method("time_bin_corr")
        path = self._directory(directory)
        method.callback_directory_select(None, {"current_path": str(path)})
        if not method.files:
            raise CommandError(
                f"No supported time-binned data files found in: {path}"
            )
        output = self._directory(arguments.get("output_directory", path))
        method.callback_save_path(None, {"current_path": str(output)})
        if self.dpg.does_item_exist("No_data_files"):
            self.dpg.delete_item("No_data_files")
        return self.time_bin_get_state({})

    def time_bin_select_file(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute time bin select file and return the documented result."""
        (filename,) = self._require_arguments(arguments, "filename")
        method = self._method("time_bin_corr")
        if filename not in method.files:
            raise CommandError(f"File is not loaded: {filename}")
        self.dpg.set_value("file_box", filename)
        method.callback_listbox("file_box", filename)
        return self.time_bin_get_state({})

    def time_bin_set_parameters(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute time bin set parameters and return the documented result."""
        method = self._method("time_bin_corr")
        tags = {
            "time_bin": "left_panel_drag_time_binning",
            "points": "left_panel_drag_subs",
            "chunks": "left_panel_N_chunks",
            "tau_min": "left_panel_tau_min",
            "tau_max": "left_panel_tau_max",
            "cross_correlation": "FCS_cross_check",
        }
        self._set_known_values(arguments, tags)
        if "time_bin" in arguments:
            method.callback_left_panel_drag_time_binning(
                tags["time_bin"], arguments["time_bin"]
            )
        elif "chunks" in arguments:
            method.on_chunks_released(None, None)
        if "cross_correlation" in arguments:
            required_results = {'result_ACF_1'}
            if method.IsTwoChannel:
                required_results.update(
                    {'result_ACF_2', 'result_CCF_1', 'result_CCF_2'}
                )
            if required_results.issubset(method.res_to_exp):
                method.callback_crossCorr_check(
                    tags["cross_correlation"],
                    bool(arguments["cross_correlation"]),
                )
        return self.time_bin_get_state({})

    def time_bin_forget_current_measurement(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute time bin forget current measurement and return the documented result."""
        method = self._method("time_bin_corr")
        method.callback_Forget_PTU_data()
        return self.time_bin_get_state({})

    def time_bin_forget_all_measurements(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute time bin forget all measurements and return the documented result."""
        method = self._method("time_bin_corr")
        method.callback_Forget_all_PTU_data()
        return self.time_bin_get_state({})

    def time_bin_set_custom_chunks(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute time bin set custom chunks and return the documented result."""
        (positions,) = self._require_arguments(arguments, "positions")
        if not isinstance(positions, list) or not positions:
            raise CommandError("positions must be a non-empty array.")
        normalized = []
        previous_stop = None
        for index, position in enumerate(positions, start=1):
            if not isinstance(position, dict):
                raise CommandError("Each chunk position must be an object.")
            if "start" not in position or "stop" not in position:
                raise CommandError(
                    f"Chunk {index} requires start and stop values."
                )
            start = float(position["start"])
            stop = float(position["stop"])
            if start < 0 or start >= stop:
                raise CommandError(
                    f"Invalid boundaries for chunk {index}: {start}, {stop}."
                )
            if previous_stop is not None and start < previous_stop:
                raise CommandError("Custom chunks must not overlap.")
            normalized.append((start, stop))
            previous_stop = stop

        method = self._method("time_bin_corr")
        maximum = float(method.TT_xdata_1[-1])
        if normalized[-1][1] > maximum:
            raise CommandError(
                f"Custom chunk stop exceeds measurement duration {maximum}."
            )
        self.dpg.set_value("Custom_chunks_check", True)
        self.dpg.set_value("left_panel_N_chunks", len(normalized))
        method.add_chunks()
        time_bin = float(self.dpg.get_value("left_panel_drag_time_binning"))
        two_channels = bool(method.IsTwoChannel)
        for index, (start, stop) in enumerate(normalized, start=1):
            start_index = max(
                0, min(len(method.TT_xdata_1) - 1, round(start / time_bin))
            )
            stop_index = max(
                start_index + 1,
                min(len(method.TT_xdata_1) - 1, round(stop / time_bin)),
            )
            effective_start = float(method.TT_xdata_1[start_index])
            effective_stop = float(method.TT_xdata_1[stop_index])
            method.chunks[f"chunk_{index - 1}"]["values"] = [
                effective_start,
                effective_stop,
            ]
            method.chunks[f"chunk_{index - 1}"]["indices"] = [
                start_index,
                stop_index,
            ]
            for channel in (1, 2) if two_channels else (1,):
                self.dpg.set_value(
                    f"Chunk_{channel}_{index}_start_dragline",
                    effective_start,
                )
                self.dpg.set_value(
                    f"Chunk_{channel}_{index}_stop_dragline",
                    effective_stop,
                )
        method.show_chunks_drag_lines("Custom_chunks_check", True)
        method.calculate_shade()
        method.plot_TT()
        return self.time_bin_get_state({})

    def time_bin_correlate_current(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute time bin correlate current and return the documented result."""
        method = self._method("time_bin_corr")
        method.correlate("Correlate_once_button", None)
        return self.time_bin_get_state({})

    def time_bin_correlate_all(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute time bin correlate all and return the documented result."""
        method = self._method("time_bin_corr")
        method.correlate_all("Correlate_all_button", None)
        return self.time_bin_get_state({})

    def time_bin_get_state(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute time bin get state and return the documented result."""
        method = self._method("time_bin_corr")
        output_path = getattr(method, "output_path", None)
        return {
            "directory": getattr(method, "last_directory", None),
            "output_directory": output_path,
            "files": list(getattr(method, "files", {}).keys()),
            "selected_file": getattr(method, "anal_file", None),
            "parameters": self._read_values(
                {
                    "time_bin": "left_panel_drag_time_binning",
                    "points": "left_panel_drag_subs",
                    "chunks": "left_panel_N_chunks",
                    "tau_min": "left_panel_tau_min",
                    "tau_max": "left_panel_tau_max",
                    "cross_correlation": "FCS_cross_check",
                }
            ),
            "custom_chunks": {
                "enabled": bool(self.dpg.get_value("Custom_chunks_check")),
                "positions": [
                    {
                        "start": chunk["values"][0],
                        "stop": chunk["values"][1],
                    }
                    for chunk in getattr(method, "chunks", {}).values()
                ],
            },
            "outputs": (
                sorted(
                    str(item)
                    for item in Path(output_path).rglob("*_corr.dat")
                    if item.is_file()
                )
                if output_path and Path(output_path).is_dir()
                else []
            ),
        }

    def _set_known_values(
        self, arguments: dict[str, Any], tags: dict[str, str]
    ) -> None:
        """Support internal set known values processing without changing public API."""
        unknown = sorted(set(arguments) - set(tags))
        if unknown:
            raise CommandError(f"Unknown parameters: {', '.join(unknown)}")
        for name, value in arguments.items():
            self.dpg.set_value(tags[name], value)

    def _read_values(self, tags: dict[str, str]) -> dict[str, Any]:
        """Support internal read values processing without changing public API."""
        return {
            name: self.dpg.get_value(tag)
            for name, tag in tags.items()
            if self.dpg.does_item_exist(tag)
        }


def register_gui_commands(
    registry: CommandRegistry,
    dpg: Any,
    context_provider: ContextProvider,
) -> FcsITGuiCommands:
    """Execute register gui commands and return the documented result."""
    commands = FcsITGuiCommands(dpg, context_provider)
    commands.register_all(registry)
    return commands
