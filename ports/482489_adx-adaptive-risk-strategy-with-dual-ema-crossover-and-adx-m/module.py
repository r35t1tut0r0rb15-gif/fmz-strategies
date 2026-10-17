"""Closes crossing the EMA 50 in an EMA 50 / 200 trend with ADX at or above 25 and DI agreeing, with the stop 0.5 ATR
beyond the 5-bar extreme and a 1.5 R target, three-minute bars.
Port of FMZ strategy #482489 "双均线趋势交叉结合ADX动量过滤的自适应风险策略-Adaptive-Risk-Strategy-with-Dual-EMA-Crossover-and-ADX-Momentum-Filter" (XAUUSD 15m Trend Strategy).

FMZ source id: 482489

Source
    https://www.fmz.com/strategy/482489 (PineScript v5, FMZ last modified 2025-02-18 16:21:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 90-123), EMA 50 / 200, DMI 14 / ADX 14 >= 25, swing 5, RR 1.5, ATR 14
    uptrend = ema50 > ema200 and adx >= 25 and +DI > -DI; long = uptrend and crossover(close, ema50)
    exit(stop = lowest(low, 5) - 0.5 ATR, limit = close + 1.5 (close - stop)); short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: (close - lowest(low, 5) + 0.5 ATR) / close and 1.5 x
      that for longs, mirrored for shorts, picked by the signal's side, shifted one bar inside stops() and re-based
      on the fill (house rule).
    * The title says XAUUSD 15m; the backtest header runs 3-minute bars, used here. DMI / ADX as #426579.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "3min".

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, EMAs, DMI / ADX, swing extremes and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, margin 100; the bracket via stops(), quoted in original_sizing.txt.
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

NAME = "fmz_482489_ema50_200_adx_ema50_cross_swing_atr_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_min": [25.0, 20.0],
    "rr": [1.5, 2.5],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200, "adx_min": 25.0, "lookback": 5, "rr": 1.5}


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


def _parts(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    dip, dim, adx = _adx_pine(bars_df, 14, 14)
    strong = adx >= p["adx_min"]
    long_e = ((f > s) & strong & (dip > dim) & (c > f) & (c.shift(1) <= f.shift(1))).astype(bool)
    short_e = ((f < s) & strong & (dim > dip) & (c < f) & (c.shift(1) >= f.shift(1))).astype(bool)
    atr = _atr(bars_df, 14)
    n = int(p["lookback"])
    sl = ((c - (lo.rolling(n).min() - 0.5 * atr)) / c).where(long_e, (h.rolling(n).max() + 0.5 * atr - c) / c)
    return long_e, short_e, sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _ = _parts(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl = _parts(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": (p["rr"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}
