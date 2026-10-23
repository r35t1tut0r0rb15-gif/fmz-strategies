"""Hourly bars, long only: the RSI 14 of hlc3 under its lower band (SMA 14 of the RSI minus 2 standard deviations over 50 bars) on a red candle goes long; the RSI above its upper band on a green candle closes, and so does the first green candle without a band signal.
Port of FMZ strategy #434449 "BB Percentage Index Trend Fading Strategy" (BB%/MFI/RSI (Noro)).

FMZ source id: 434449

Source
    https://www.fmz.com/strategy/434449 (PineScript v2, FMZ last modified 2023-12-06 14:43:39).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 128-196), RSI 14 of hlc3 (Draw RSI on, MFI off); band basis SMA 14, deviation 2 x stdev 50; long on, short off; lot 100 %; pyramiding 100
    up = bb_s < lower and close < open;  dn = bb_s > upper and close > open;  exit = not up and not dn and (long and close > open or short and close < open)
    up -> (close short) entry Long;  dn -> close_all (long), entry Short with qty 0 (short off);  exit -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * With "Draw RSI" on and "Draw MFI" off, the bands are drawn on the RSI and the money-flow lines are
      never computed: volume is not used. The short entry has qty 0 (Short off), so dn only closes a long.
      pyramiding 100 lets every further "up" bar add a lot while long: adds are sizing, the port keeps one
      position (as earlier ports). The basis is an SMA 14 and the deviation a 50-bar stdev (population),
      as written. The date window (1900 .. 2100) is dropped. Long only. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI Bollinger-band reversals with a first-green-bar exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: lot = equity / close x 100 %, pyramiding 100 (adds), not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the 1900 .. 2100 window dropped).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434449_rsi14_bollinger_band_red_bar_first_green_exit_long"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 14, "mult": 2.0, "bb_len": 50}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    r = _rsi((h + lo + c) / 3, n)
    basis = r.rolling(n).mean()
    dev = float(p["mult"]) * r.rolling(int(p["bb_len"])).std(ddof=0)
    up = ((r < basis - dev) & (c < o)).to_numpy()
    dn = ((r > basis + dev) & (c > o)).to_numpy()
    green = (c > o).to_numpy()
    m = len(up)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if up[i]:
            if pos == 0:
                le[i], pos = True, 1
        elif pos == 1 and (dn[i] or green[i]):
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
