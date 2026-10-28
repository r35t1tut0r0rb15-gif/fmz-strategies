"""Registration and input/output plumbing shared by every indicator.

Each indicator is written once as a *core* function that takes 2D float
arrays (inputs first, then parameters) and returns one array or a tuple of
arrays. ``@indicator`` turns a core into:

* a user-facing function that accepts ``pd.Series``, ``pd.DataFrame`` or numpy
  arrays and returns the same type (a namedtuple when there are several
  outputs), and
* an entry in ``REGISTRY`` from which ``tv_indicators.vbt`` builds a
  vectorbt ``IndicatorFactory`` class with the same inputs, params and outputs.
"""

import functools
import inspect
from collections import namedtuple

import numpy as np
import pandas as pd

from . import kernels as k

REGISTRY = {}


def _to_2d(x):
    if isinstance(x, pd.Series):
        return x.to_numpy(dtype=float).reshape(-1, 1)
    if isinstance(x, pd.DataFrame):
        return x.to_numpy(dtype=float)
    a = np.asarray(x, dtype=float)
    return a.reshape(-1, 1) if a.ndim <= 1 else a


def f2d(x):
    """Make sure a core receives a C-contiguous 2D float64 array."""
    return np.ascontiguousarray(_to_2d(x), dtype=np.float64)


def _broadcast(arrays):
    rows = max(a.shape[0] for a in arrays)
    width = max(a.shape[1] for a in arrays)
    return [np.ascontiguousarray(np.broadcast_to(a, (rows, width))) for a in arrays]


def _wrap(arr, like, name):
    if isinstance(like, pd.DataFrame):
        return pd.DataFrame(arr, index=like.index, columns=like.columns)
    if isinstance(like, pd.Series):
        if arr.shape[1] == 1:
            return pd.Series(arr[:, 0], index=like.index, name=name)
        return pd.DataFrame(arr, index=like.index)
    if np.ndim(like) == 1 and arr.shape[1] == 1:
        return arr[:, 0]
    return arr


def _pick_template(values):
    pandas = [v for v in values if isinstance(v, (pd.Series, pd.DataFrame))]
    if not pandas:
        return values[0]
    return max(pandas, key=lambda v: 1 if isinstance(v, pd.Series) else v.shape[1])


def indicator(name, inputs, outputs):
    """Register ``core`` as indicator ``name``."""

    def deco(core):
        sig = inspect.signature(core)
        params = {p: v.default for p, v in sig.parameters.items() if p not in inputs}
        result_cls = namedtuple(name, outputs) if len(outputs) > 1 else None

        @functools.wraps(core)
        def public(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            raw = [bound.arguments[i] for i in inputs]
            arrays = _broadcast([f2d(v) for v in raw])
            res = core(*arrays, **{p: bound.arguments[p] for p in params})
            if not isinstance(res, tuple):
                res = (res,)
            like = _pick_template(raw)
            wrapped = [_wrap(r, like, outputs[j]) for j, r in enumerate(res)]
            return result_cls(*wrapped) if result_cls else wrapped[0]

        public.core = core
        public.inputs = list(inputs)
        public.outputs = list(outputs)
        public.params = params
        REGISTRY[name] = public
        return public

    return deco


# ---------------------------------------------------------------------------
# Moving-average dispatch used by several indicators
# ---------------------------------------------------------------------------

_MA_ALIASES = {
    "sma": "sma",
    "ema": "ema",
    "rma": "rma",
    "smma": "rma",
    "smma (rma)": "rma",
    "wilder": "rma",
    "wma": "wma",
    "vwma": "vwma",
    "hma": "hma",
    "hull": "hma",
    "dema": "dema",
    "tema": "tema",
    "lsma": "lsma",
    "linreg": "lsma",
}


def ma_kind(ma_type):
    try:
        return _MA_ALIASES[str(ma_type).strip().lower()]
    except KeyError:
        raise ValueError(f"unknown ma_type {ma_type!r}; use one of {sorted(set(_MA_ALIASES))}")


def hma_2d(x, n):
    half = k.wma_nb(x, max(int(n // 2), 1))
    full = k.wma_nb(x, n)
    return k.wma_nb(2 * half - full, max(int(np.floor(np.sqrt(n) + 0.5)), 1))


def ma_2d(x, n, ma_type="sma", volume=None):
    """Moving average of 2D array ``x`` picked by name (TradingView names work)."""
    n = int(n)
    kind = ma_kind(ma_type)
    if kind == "sma":
        return k.sma_nb(x, n)
    if kind == "ema":
        return k.ema_nb(x, n)
    if kind == "rma":
        return k.rma_nb(x, n)
    if kind == "wma":
        return k.wma_nb(x, n)
    if kind == "vwma":
        if volume is None:
            raise ValueError("ma_type='vwma' needs volume")
        return k.sma_nb(x * volume, n) / k.sma_nb(volume, n)
    if kind == "hma":
        return hma_2d(x, n)
    if kind == "dema":
        e1 = k.ema_nb(x, n)
        return 2 * e1 - k.ema_nb(e1, n)
    if kind == "tema":
        e1 = k.ema_nb(x, n)
        e2 = k.ema_nb(e1, n)
        return 3 * (e1 - e2) + k.ema_nb(e2, n)
    if kind == "lsma":
        return k.linreg_nb(x, n, 0)
    raise AssertionError(kind)


def change_2d(x, n=1):
    """``ta.change(x, n)``."""
    out = np.full(x.shape, np.nan)
    out[n:] = x[n:] - x[:-n]
    return out


def shift_2d(x, n=1):
    """``x[n]`` in Pine: the value ``n`` bars ago (negative ``n`` shifts forward)."""
    out = np.full(x.shape, np.nan)
    if n > 0:
        out[n:] = x[:-n]
    elif n < 0:
        out[:n] = x[-n:]
    else:
        out[:] = x
    return out


def safe_div(a, b):
    """Division where x/0 gives na, like Pine."""
    with np.errstate(divide="ignore", invalid="ignore"):
        out = a / b
    out[~np.isfinite(out)] = np.nan
    return out
