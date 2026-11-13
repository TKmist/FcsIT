# Changelog

This file summarises the main changes in the current `V2.0.2` working tree relative to the `main` branch (`v1.0.0rc5`).

## V2.0.2

- Exposed bootstrap block length and segment count controls in the PTU/PT3 and Time-binned correlation interfaces, with validation that keeps the block length below half the segment count. `L=1` performs ordinary non-parametric resampling of complete segment-wise curves, whereas `L>1` performs circular-block resampling of consecutive segments.
- Added a Time-binned multi-tau compression selector (`average` or `first`), enforced a minimum lag time no shorter than the input bin width, and kept effective lag grids within the range supported by the data.
- Separated the PTU display time bin from correlation settings, added automatic display-bin adjustment and plot downsampling for large traces, and improved recovery from memory and batch-processing failures.
- Added persistent `runtime_log.txt` diagnostics for Python exceptions and fatal errors while preserving terminal error output.
- Hardened fitting against missing, zero, or non-finite error values; corrected fitted-range handling, residual plotting, brightness restoration, stored-result synchronisation, and mean brightness, reduced-chi-square, and p-value statistics.
- Improved correlation action-state restoration and prevented duplicate single-file PTU correlation runs.
- Updated terminology from chunks to segments and documented the V2.0.2 bootstrap block-length, multi-tau compression, data-driven lag, and TCP/JSON controls.
- Extended TCP/JSON `set_parameters` and `get_state` support for bootstrap block length and Time-binned multi-tau compression. Long-running client calls now wait for a terminal response without a response timeout.

## V2.0.1

- Fixed the **Calculate filter** callback and ensured that enabled TCSPC filtering is executed.
- Fixed PIE detection, the default channel-1 lifetime gate, and exclusion of photons outside the selected gate.
- Added automatic documentation building and installation during Linux and Windows installation and updates.

## V2.0.0

- Reworked installation and updates, including manifest-driven dependency migration, platform launchers, and update payload handling.
- Replaced the legacy PicoQuant reader with `phconvert`, adding PTU and PT3 support while retaining T2 continuous-wave measurements without TCSPC gating.
- Added circular-block-bootstrap lag covariance, robust handling of unequal segments and missing long-lag values, and covariance-aware sandwich parameter errors for new `.corr` files.
- Added automatic `.dat` and `.corr` export and platform-safe parallel processing to the Time-binned correlation module.
- Added a localhost-only TCP/JSON command server, Linux and Windows `fcsit_call` clients, command discovery, and scripted fitting, PTU/PT3, and Time-binned workflows.
- Extended settings, themes, result export controls, and application update status handling.
