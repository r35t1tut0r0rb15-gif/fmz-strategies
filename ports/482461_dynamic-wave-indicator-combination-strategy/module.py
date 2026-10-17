"""MACD signal crosses beyond the EMA 200 with ADX above 20 and RSI on the same side of 50, with a 1.5 ATR stop and a
2 R target, three-hour bars.
Port of FMZ strategy #482461 "动态波浪指标组合策略-Dynamic-Wave-Indicator-Combination-Strategy" (Optimized Impulse Wave Strategy).

FMZ source id: 482461

Source
    https://www.fmz.com/strategy/482461 (PineScript v5, FMZ last modified 2025-02-18 15:20:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-138), MACD 12 / 26 / 9, EMA 200, RSI 14, DMI / ADX 14 (> 20),
ATR 14 x 1.5, RR 2
    crossover(macd, signal) and close > ema200 and adx > 20 and rsi > 50 -> entry long with
    exit(limit = close + 3 ATR, stop = close - 1.5 ATR); short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: 1.5 ATR / close and RR x that, shifted one bar inside
      stops() and re-based on the fill (house rule). DMI / ADX as #426579.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "3h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, MACD, an EMA, ADX, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
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

NAME = "fmz_482461_macd_cross_ema200_adx_rsi_atr_rr"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_min": [20.0, 25.0],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"ema_len": 200, "rsi_len": 14, "adx_len": 14, "atr_len": 14, "adx_min": 20.0, "rr": 2.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    _, _, adx = _adx_pine(bars_df, int(p["adx_len"]), int(p["adx_len"]))
    strong = adx > p["adx_min"]
    long_e = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (c > ema) & strong & (rsi > 50)).astype(bool)
    short_e = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & (c < ema) & strong & (rsi < 50)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (1.5 * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
