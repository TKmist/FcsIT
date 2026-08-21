"""
Copyright (C) 2026 Tomasz Kalwarczyk (https://github.com/TKmist)

This file is part of the FcsIT repository.

This file is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later version.

This file is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with this file. If not, see <https://www.gnu.org/licenses/>.
"""


"""Post-hoc covariance-aware parameter errors for an existing LM fit."""

import numpy as np


def _finite_difference_jacobian(model_result, x, parameter_names):
    """Evaluate the model Jacobian without changing the fitting engine."""
    x = np.asarray(x, dtype=float)
    jacobian = np.empty((x.size, len(parameter_names)), dtype=float)
    base = model_result.params.copy()

    for column, name in enumerate(parameter_names):
        parameter = base[name]
        value = float(parameter.value)
        step = np.sqrt(np.finfo(float).eps) * max(abs(value), 1.0)
        lower = max(value - step, float(parameter.min))
        upper = min(value + step, float(parameter.max))
        if not np.isfinite(lower):
            lower = value - step
        if not np.isfinite(upper):
            upper = value + step
        if upper <= lower:
            jacobian[:, column] = 0.0
            continue

        plus = base.copy()
        minus = base.copy()
        plus[name].set(value=upper)
        minus[name].set(value=lower)
        y_plus = np.asarray(model_result.model.eval(params=plus, x=x), dtype=float)
        y_minus = np.asarray(model_result.model.eval(params=minus, x=x), dtype=float)
        jacobian[:, column] = (y_plus - y_minus) / (upper - lower)

    return jacobian


def sandwich_standard_errors(model_result, x, sigma, lag_covariance):
    """Return HC-style sandwich errors using a supplied lag covariance matrix.

    The fitted parameters and objective remain those obtained by lmfit/LM.
    Only their post-hoc covariance is replaced by A^-1 B A^-1, where the
    middle matrix contains the covariance between lag-time observations.
    """
    x = np.asarray(x, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    omega = np.asarray(lag_covariance, dtype=float)
    if omega.shape != (x.size, x.size):
        raise ValueError("Lag covariance dimensions do not match fitted data.")
    if sigma.shape != (x.size,):
        raise ValueError("Pointwise standard errors do not match fitted data.")
    if np.any(~np.isfinite(omega)) or np.any(~np.isfinite(sigma)):
        raise ValueError("Covariance inputs contain non-finite values.")
    if np.any(sigma <= 0.0):
        raise ValueError("Pointwise standard errors must be positive.")

    parameter_names = [
        name for name, parameter in model_result.params.items()
        if parameter.vary and parameter.expr is None
    ]
    if not parameter_names:
        return {}, np.empty((0, 0), dtype=float)

    jacobian = _finite_difference_jacobian(
        model_result, x, parameter_names
    )
    precision = 1.0 / np.square(sigma)
    bread = jacobian.T @ (precision[:, None] * jacobian)
    bread_inverse = np.linalg.pinv(bread, hermitian=True)
    weighted_omega = precision[:, None] * omega * precision[None, :]
    meat = jacobian.T @ weighted_omega @ jacobian
    covariance = bread_inverse @ meat @ bread_inverse
    covariance = 0.5 * (covariance + covariance.T)
    diagonal = np.clip(np.diag(covariance), 0.0, None)
    errors = {
        name: float(error)
        for name, error in zip(parameter_names, np.sqrt(diagonal))
    }
    return errors, covariance
