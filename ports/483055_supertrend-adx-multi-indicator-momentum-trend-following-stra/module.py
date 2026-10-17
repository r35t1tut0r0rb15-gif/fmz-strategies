"""Supertrend (14, 3) up-trend with ADX above 14 and RSI away from 50, long only, closed when the Supertrend turns
down, 5-minute bars.
Port of FMZ strategy #483055 "多指标交叉动量趋势跟踪策略基于Supertrend与ADX双重确认的量化交易系统-Multi-Indicator-Momentum-Trend-Following-Strategy-Quantitative-Trading-System-Based-on-Supertrend-and-ADX-Dual-Confirmation" (Supertrend + ADX Strategy).

FMZ source id: 483055

Source
    https://www.fmz.com/strategy/483055 (PineScript v6, FMZ last modified 2025-02-27 17:07:46).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 119-157), DMI 14 / 14, ADX > 14, RSI 14, Supertrend 3 / 14
    long = direction == -1 and adx > 14 and (rsi < 40 or rsi > 60) -> entry long
    exit = direction == 1 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend as TradingView documents it (direction -1 = up-trend); ADX as Pine's ta.dmi (as #426579).
    * Every bar in the condition is an entry signal (same-side ignored while held); the entry and exit conditions
      exclude each other. Long only; the source has no shorts. No stops. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Supertrend (ATR bands), ADX and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483055_supertrend_up_adx_rsi_long"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "adx_min": [14.0, 25.0],
}
DEFAULT_PARAMS = {"di_len": 14, "adx_len": 14, "adx_min": 14.0, "factor": 3.0, "st_len": 14, "rsi_len": 14}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


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


def _supertrend_dir(bars_df, factor, n):
    """ta.supertrend direction (pine_supertrend): -1 up-trend, 1 down-trend; nan comparisons are false."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    dr = np.ones(m)
    prev_u = prev_l = prev_st = np.nan
    for i in range(m):
        up, lw = src[i] + factor * atr[i], src[i] - factor * atr[i]
        pl = 0.0 if np.isnan(prev_l) else prev_l
        pu = 0.0 if np.isnan(prev_u) else prev_u
        pc = c[i - 1] if i > 0 else np.nan
        lw = lw if (lw > pl or pc < pl) else pl
        up = up if (up < pu or pc > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif prev_st == pu:
            d = -1 if c[i] > up else 1
        else:
            d = 1 if c[i] < lw else -1
        dr[i] = d
        prev_u, prev_l, prev_st = up, lw, (lw if d == -1 else up)
    return dr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    _, _, adx = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_len"]))
    rsi = _rsi(c, int(p["rsi_len"]))
    d = pd.Series(_supertrend_dir(bars_df, float(p["factor"]), int(p["st_len"])), index=c.index)
    long_e = ((d == -1) & (adx > p["adx_min"]) & ((rsi < 40) | (rsi > 60))).astype(bool)
    long_x = (d == 1).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
