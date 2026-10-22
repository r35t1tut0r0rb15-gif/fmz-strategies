"""Keltner channel (EMA 21 +- 2 ATR 13) reversion, 1-hour bars, long only: a close under the lower band buys; a bar opening over the upper band sells.
Port of FMZ strategy #453223 "Keltner-Channels-EMA-ATR-Strategy-Keltner通道EMA-ATR策略" (Keltner Channel Strategy).

FMZ source id: 453223

Source
    https://www.fmz.com/strategy/453223 (PineScript v5, FMZ last modified 2024-06-03 10:39:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-124), EMA 21; ATR 13 x 2; 10 % of equity (strategy() declared last)
    not in_trade and close < lower -> entry Long, in_trade = true;  in_trade and open > upper -> close Long, in_trade = false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The in_trade flag is followed as written beside the position: it is set by each entry call and
      cleared by each close call, so on a bar that both enters and closes (a huge bar) the close finds
      no trade yet, the flag is cleared and the long fills anyway, to be closed on a later bar opening
      over the upper band after the flag is set again. The upper-band test uses the bar's own open
      against the band at its close. Long only. The 10 % of equity is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Keltner lower-band dips with an upper-band exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453223_keltner21_lower_close_upper_open_exit_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 50],
    "mult": [2.0, 3.0],
    "atr_len": [13, 20],
}
DEFAULT_PARAMS = {"length": 21, "mult": 2.0, "atr_len": 13}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    ema = c.ewm(span=int(p["length"]), adjust=False).mean()
    atr = _atr(bars_df, p["atr_len"])
    k = float(p["mult"])
    dip = (c < ema - k * atr).to_numpy()
    out = (o > ema + k * atr).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    flag, pos, pend = False, 0, 0
    for i in range(m):
        if pend == 1:
            pos = 1
        elif pend == 2:
            pos = 0
        pend = 0
        if not flag and dip[i]:
            flag = True
            if pos == 0:
                le[i], pend = True, 1
        if flag and out[i]:
            flag = False
            if pos == 1:
                lx[i], pend = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
