"""Hourly bars: the first bar of the volume-weighted averages stacked up (VWMA 20 > 50 > 100) with an RSI 30 under 50 goes long, the first bar stacked down with the RSI above 48.5 goes short; each position closes three bars after its signal unless an opposite signal reversed it.
Port of FMZ strategy #439103 "Dual Moving Average Golden Cross Strategy" (EA_3Minute_MagnetStrat).

FMZ source id: 439103

Source
    https://www.fmz.com/strategy/439103 (PineScript v4, FMZ last modified 2024-01-17 17:38:36).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 156-197), RSI 30 (rma); VWMA 20 / 50 / 100; RSI 50 / 48.5; close 3 bars after the signal
    long1 = ma20 > ma50 and ma50 > ma100 and rsi < 50;  short1 = ma20 < ma50 and ma50 < ma100 and rsi > 48.5;  long = long1[1] == 0 and long1 == 1;  short likewise
    entry short (qty 1) when short;  entry long (qty 1) when long;  close long when long[3];  close short when short[3]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages are vwma(close, n) = sma(close x volume, n) / sma(volume, n). The entries are
      called short first, long second (a two-sided bar cannot occur: the stacks exclude each other). A
      close acts only on a position the bar's entries leave unchanged; it closes whatever position of that
      side is open three bars after the signal bar. REVERSAL INTENDED. qty 1 is sizing. FREQ = "1h" from
      the backtest header (the title says 3 minutes).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stacked volume-weighted averages with an RSI filter, fixed 3-bar hold.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: entry qty 1 unit, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the weights of the three VWMAs; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439103_vwma_stack_rsi30_edge_3bar_hold_1h_reversal"
FAMILY = "volume_weighted_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hold_bars": [3, 6],
    "rsi_len": [30, 14],
}
DEFAULT_PARAMS = {"rsi_len": 30, "ma1": 20, "ma2": 50, "ma3": 100, "rsi_long": 50.0, "rsi_short": 48.5,
                  "hold_bars": 3}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    d = c.diff()
    n = int(p["rsi_len"])
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = (100 - 100 / (1 + up / dn.where(dn != 0))).where(up != 0, 0.0).where(dn != 0, 100.0)
    rsi = rsi.where(up.notna() & dn.notna())

    def vwma(k):
        sv = v.rolling(k).mean()
        return (c * v).rolling(k).mean() / sv.where(sv != 0)

    m1, m2, m3 = vwma(int(p["ma1"])), vwma(int(p["ma2"])), vwma(int(p["ma3"]))
    l1 = ((m1 > m2) & (m2 > m3) & (rsi < float(p["rsi_long"]))).to_numpy()
    s1 = ((m1 < m2) & (m2 < m3) & (rsi > float(p["rsi_short"]))).to_numpy()
    valid = (m3.notna() & rsi.notna()).to_numpy()
    prev_ok = np.concatenate(([False], valid[:-1]))
    lg = l1 & prev_ok & ~np.concatenate(([False], l1[:-1]))
    sh = s1 & prev_ok & ~np.concatenate(([False], s1[:-1]))
    k = int(p["hold_bars"])
    m = len(lg)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if sh[i] and new != -1:
            new = -1
        if lg[i] and new != 1:
            new = 1
        if new == pos and i >= k:
            if pos == 1 and lg[i - k]:
                new = 0
            elif pos == -1 and sh[i - k]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
