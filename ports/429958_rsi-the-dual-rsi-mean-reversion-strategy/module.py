"""RSI extreme with a Heikin Ashi colour turn, hourly bars: two green HA candles after RSI 14 was below 30 within the last
3 bars go long; two red HA candles after RSI 14 was above 70 go short.
Port of FMZ strategy #429958 "双向RSI均线回复策略The-Dual-RSI-Mean-Reversion-Strategy" (Gidra's Vchain Strategy v0.1).

FMZ source id: 429958

Source
    https://www.fmz.com/strategy/429958 (PineScript v2, FMZ last modified 2023-10-23 15:46:33).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 146-213), RSI 14, limit 30, 3 signal bars, open-colour filter 2 bars
    rsidnok = highest(rsi < 30, 3) == 1; rsiupok = highest(rsi > 70, 3) == 1
    up = sma(HA green, 2) == 1 and rsidnok -> entry long; dn = sma(HA red, 2) == 1 and rsiupok -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * HA open / close as the source (haopen = previous (haopen + haclose) / 2). pyramiding 100: repeated
      entries are adds (sizing, not ported). The date window and its close_all are dropped.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and candle colours only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 100 and the lot formula stored.
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

NAME = "fmz_429958_rsi_extreme_ha_turn"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_limit": [30, 20],
    "rsi_bars": [3, 5],
}
DEFAULT_PARAMS = {"rsi_period": 14, "rsi_limit": 30, "rsi_bars": 3, "open_bars": 2}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    cs = bars_df["close"]
    hc = (o + h + lo + c) / 4
    m = len(c)
    ho = np.full(m, np.nan)
    for i in range(m):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 or np.isnan(ho[i - 1]) else (ho[i - 1] + hc[i - 1]) / 2
    idx = bars_df.index
    green = pd.Series((hc > ho).astype(float), index=idx)
    red = pd.Series((hc < ho).astype(float), index=idx)
    d = cs.diff()
    n = int(p["rsi_period"])
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = pd.Series(np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn))), index=idx)
    rsi = rsi.where(up.notna() & dn.notna())
    lim, nb = float(p["rsi_limit"]), int(p["rsi_bars"])
    dn_ok = (rsi < lim).astype(float).rolling(nb).max() == 1
    up_ok = (rsi > 100 - lim).astype(float).rolling(nb).max() == 1
    ob = int(p["open_bars"])
    long_e = ((green.rolling(ob).mean() == 1) & dn_ok).astype(bool)
    short_e = ((red.rolling(ob).mean() == 1) & up_ok).astype(bool)
    false = pd.Series(False, index=idx)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
