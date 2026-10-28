"""Pivot Points Standard (TradingView built-in) from the previous period."""

import numpy as np
import pandas as pd
from numba import njit

from ._core import f2d, indicator
from .volume import session_ids

NAN = np.nan
_KINDS = {"traditional": 0, "fibonacci": 1, "woodie": 2, "classic": 3, "camarilla": 4}


@njit(cache=True)
def _pivots_nb(open_, high, low, close, session, kind):
    shape = close.shape
    outs = np.full((7,) + shape, NAN)
    for c in range(shape[1]):
        ch = NAN
        cl = NAN
        cc = NAN
        ph = NAN
        pl = NAN
        pc = NAN
        cur_open = NAN
        for i in range(shape[0]):
            if i == 0 or session[i, c] != session[i - 1, c]:
                if i > 0:
                    ph, pl, pc = ch, cl, cc
                ch = high[i, c]
                cl = low[i, c]
                cur_open = open_[i, c]
            else:
                ch = max(ch, high[i, c])
                cl = min(cl, low[i, c])
            cc = close[i, c]
            if np.isnan(pc):
                continue
            h, lo, cl_ = ph, pl, pc
            r = h - lo
            if kind == 2:
                p = (h + lo + 2 * cur_open) / 4
            else:
                p = (h + lo + cl_) / 3
            if kind == 0:  # traditional
                r1, s1 = 2 * p - lo, 2 * p - h
                r2, s2 = p + r, p - r
                r3, s3 = 2 * p + (h - 2 * lo), 2 * p - (2 * h - lo)
            elif kind == 1:  # fibonacci
                r1, s1 = p + 0.382 * r, p - 0.382 * r
                r2, s2 = p + 0.618 * r, p - 0.618 * r
                r3, s3 = p + r, p - r
            elif kind == 2:  # woodie
                r1, s1 = 2 * p - lo, 2 * p - h
                r2, s2 = p + r, p - r
                r3, s3 = h + 2 * (p - lo), lo - 2 * (h - p)
            elif kind == 3:  # classic
                r1, s1 = 2 * p - lo, 2 * p - h
                r2, s2 = p + r, p - r
                r3, s3 = p + 2 * r, p - 2 * r
            else:  # camarilla
                r1, s1 = cl_ + 1.1 * r / 12, cl_ - 1.1 * r / 12
                r2, s2 = cl_ + 1.1 * r / 6, cl_ - 1.1 * r / 6
                r3, s3 = cl_ + 1.1 * r / 4, cl_ - 1.1 * r / 4
            vals = (p, r1, r2, r3, s1, s2, s3)
            for j in range(7):
                outs[j, i, c] = vals[j]
    return outs


@indicator("PIVOT_POINTS_SESSION", ["open", "high", "low", "close", "session"],
           ["p", "r1", "r2", "r3", "s1", "s2", "s3"])
def pivot_points_session(open, high, low, close, session, kind="traditional"):
    """Pivot levels from the previous ``session`` id's high/low/close.

    ``kind``: traditional, fibonacci, woodie, classic, camarilla. Woodie uses
    the current period's open, as TradingView does.
    """
    try:
        code = _KINDS[str(kind).lower()]
    except KeyError:
        raise ValueError(f"kind must be one of {list(_KINDS)}")
    return tuple(_pivots_nb(open, high, low, close, session, code))


def pivot_points(open, high, low, close, anchor="D", kind="traditional"):
    """Pivot Points Standard, anchored by period (D, W, M, Q, Y).

    Pass pandas objects with a DatetimeIndex. Levels are constant within a
    period and use only the previous, completed period.
    """
    sess = session_ids(close.index, anchor)
    width = f2d(close).shape[1]
    sess2 = np.repeat(sess.reshape(-1, 1), width, axis=1)
    if isinstance(close, pd.DataFrame):
        s = pd.DataFrame(sess2, index=close.index, columns=close.columns)
    else:
        s = pd.Series(sess, index=close.index)
    return pivot_points_session(open, high, low, close, s, kind)
