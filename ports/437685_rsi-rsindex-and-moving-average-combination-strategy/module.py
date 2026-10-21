"""Connors RSI-2 extremes with an SMA 120 trend, 1-hour bars: above the SMA 120 an RSI 2 between 1 and 10 buys, below it an RSI 2 between 90 and 98 sells (reversing); a long closes once the close is above the
SMA 5 with the close under its 3-bar SMA, a short once the close is under the SMA 5 with the close above its 2-bar SMA.
Port of FMZ strategy #437685 "阻力与支撑带动的拉里金叉RSI策略RSIndex-and-Moving-Average-Combination-Strategy" (_CM_RSI_2_Strategy_Lower).

FMZ source id: 437685

Source
    https://www.fmz.com/strategy/437685 (PineScript v2, FMZ last modified 2024-01-04 17:46:07).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 124-163), RSI 2 (rma), trend SMA 120 (named ma200), exits SMA 5 with SMA 1 / 3 / 2
    close > sma 120 and 1 < rsi < 10 -> entry RSI_2_L;  close < sma 120 and 90 < rsi < 98 -> entry RSI_2_S
    close RSI_2_L when close > sma 5 and sma 1 < sma 3;  close RSI_2_S when close < sma 5 and sma 1 > sma 2

Interpretation choices (Pine rules in SURVEY_README.md)
    * sma(close, 1) is the close. Orders follow the script's call order (entries, then the closes of the
      position open at the bar's close and left unchanged by the entries). REVERSAL INTENDED. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and SMA comparisons.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG437685 (2 members, best partner #439194, Jaccard 0.844); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437685_connors_rsi2_sma_exits"
FAMILY = "rsi_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trend_len": [120, 200],
    "exit_len": [5, 10],
}
DEFAULT_PARAMS = {"trend_len": 120, "exit_len": 5, "rsi_len": 2}


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
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    tr = c.rolling(int(p["trend_len"])).mean()
    ma5 = c.rolling(int(p["exit_len"])).mean()
    ma2, ma3 = c.rolling(2).mean(), c.rolling(3).mean()
    lc = ((c > tr) & (r < 10) & (r > 1)).to_numpy()
    sc = ((c < tr) & (r > 90) & (r < 98)).to_numpy()
    lxc = ((c > ma5) & (c < ma3)).to_numpy()
    sxc = ((c < ma5) & (c > ma2)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        s, changed = pos, False
        if lc[i] and s != 1:
            s, changed = 1, True
        if sc[i] and s != -1:
            s, changed = -1, True
        if not changed:
            if lxc[i] and pos == 1:
                s = 0
            elif sxc[i] and pos == -1:
                s = 0
        if s == 1 and pos != 1:
            le[i] = True
        elif s == -1 and pos != -1:
            se[i] = True
        elif s == 0 and pos == 1:
            lx[i] = True
        elif s == 0 and pos == -1:
            sx[i] = True
        pos = s
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
