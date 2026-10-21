"""Noro's BB + RSI dip buys, 1-hour bars, long only: from flat, the RSI 7 under 30 with the low under the lower Bollinger band (SMA 20 of ohlc4 - 2 sigma) buys; a green bar (close above open) closes the long.
Port of FMZ strategy #438007 "RSI与布林线量化交易策略RSI-and-Bollinger-Bands-Quantitative-Trading-Strategy" (BB+RSI str 1.0).

FMZ source id: 438007

Source
    https://www.fmz.com/strategy/438007 (PineScript v3, FMZ last modified 2024-01-08 10:16:22).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 141-185), lot 100 %; RSI and BB on; BB 20 x 2 on ohlc4; RSI 7 on close, limit 30; pyramiding 5; date window 1900-2100
    up = rsi(close, 7) < 30 and low < lower -> entry Long (lot);  cl = close > open -> entry Close, short, qty 0;  time after 2100-12-31 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short entry with quantity 0 only closes the long (Noro's idiom; as #435019): it acts on the
      position held at the bar close, so a bar with both signals opens a long from flat, and closes an
      open long. pyramiding 5 allows adds (sizing): the port holds one position. stdev is the population
      deviation. The 2100 close_all never fires. Long only. The equity lot is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band and RSI levels; bar colour.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity lot, pyramiding 5 and the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438007_bb_rsi_dip_buy_green_close"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsilimit": [30, 20],
    "bbperiod": [20, 40],
}
DEFAULT_PARAMS = {"rsilimit": 30.0, "bbperiod": 20, "bbmult": 2.0, "rsiperiod": 7}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    src = (o + h + lo + c) / 4.0
    n = int(p["bbperiod"])
    lower = src.rolling(n).mean() - float(p["bbmult"]) * src.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsiperiod"]))
    up = ((r < float(p["rsilimit"])) & (lo < lower)).to_numpy()
    cl = (c > o).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and cl[i]:
            lx[i], pos = True, 0
        elif pos == 0 and up[i] and i + 1 < m:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
