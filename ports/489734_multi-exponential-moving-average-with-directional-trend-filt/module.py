"""EMA 5 / 8 crosses with an EMA 13 close exit and an optional ADX filter, hourly bars: EMA 5 crossing above EMA 8
goes long, crossing below goes short; a close below EMA 13 closes the long, above it closes the short.
Port of FMZ strategy #489734 "多指数移动平均与方向性趋势过滤交易系统-Multi-Exponential-Moving-Average-with-Directional-Trend-Filter-Trading-System" ([SM-042] EMA 5-8-13 with ADX Filter).

FMZ source id: 489734

Source
    https://www.fmz.com/strategy/489734 (PineScript v5, FMZ last modified 2025-04-08 10:13:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 199-232), EMA 5 / 8 / 13, ADX 14 > 20 (filter off by default)
    long = crossover(ema5, ema8) [and adx > 20];  short = crossunder(ema5, ema8) [and adx > 20]
    position > 0 and close < ema13 -> close long;  position < 0 and close > ema13 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes test the position held at the bar's start and are written after the entries: they never undo an
      entry made on the bar (as #430850). Entries reverse (REVERSAL INTENDED).
    * The ADX filter (off by default) is a declared variant in the GRID (use_adx). DMI with Wilder smoothing and
      fixnan (as #426579). The commission in strategy() is a cost (not in the module).
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs and ADX.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489734_ema_5_8_cross_ema13_exit"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "use_adx": [False, True],
    "exit_ema": [13, 21],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 8, "exit_ema": 13, "use_adx": False, "adx_threshold": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e5 = c.ewm(span=int(p["fast"]), adjust=False).mean()
    e8 = c.ewm(span=int(p["slow"]), adjust=False).mean()
    e13 = c.ewm(span=int(p["exit_ema"]), adjust=False).mean()
    ok = (_adx_pine(bars_df, 14, 14)[2] > p["adx_threshold"]) if p["use_adx"] else pd.Series(True, index=c.index)
    long_c = ((e5 > e8) & (e5.shift(1) <= e8.shift(1)) & ok).to_numpy()
    short_c = ((e5 < e8) & (e5.shift(1) >= e8.shift(1)) & ok).to_numpy()
    below, above = (c < e13).to_numpy(), (c > e13).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if long_c[i]:
            pos = 1
        if short_c[i]:
            pos = -1
        if start == 1 and pos == 1 and below[i]:
            pos = 0
        if start == -1 and pos == -1 and above[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
