"""+DI / -DI crosses with ADX above 25, reversing, with a 1 % stop and a 2 % target from the entry, four-hour bars.
Port of FMZ strategy #482424 "动量趋势跟踪指标DMIADX交叉策略-Momentum-Trend-Following-DMIADX-Crossover-Strategy" (DMI + ADX Strategy).

FMZ source id: 482424

Source
    https://www.fmz.com/strategy/482424 (PineScript v6, FMZ last modified 2025-02-18 13:47:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 132-162), DMI 14 / ADX 14 > 25, SL 1 %, TP 2 %
    crossover(+DI, -DI) and adx > 25 -> entry long; crossunder and adx > 25 -> entry short
    while held: exit(stop / limit = position_avg_price x (1 -/+ 1 % / 2 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is measured from strategy.position_avg_price: with one entry it is the fill, applied as the house
      bracket from the fill (decision owed as #489289). DMI / ADX as #426579.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "4h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket from the fill.
    2 generic: PASS, DMI / ADX and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 250 % of equity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482424_di_cross_adx25_pct_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_min": [25.0, 20.0],
    "tp_pct": [2.0, 4.0],
}
DEFAULT_PARAMS = {"di_len": 14, "adx_len": 14, "adx_min": 25.0, "sl_pct": 1.0, "tp_pct": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dip, dim, adx = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_len"]))
    strong = adx > p["adx_min"]
    long_e = ((dip > dim) & (dip.shift(1) <= dim.shift(1)) & strong).astype(bool)
    short_e = ((dip < dim) & (dip.shift(1) >= dim.shift(1)) & strong).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
