"""RSI 3 extremes in a stacked EMA 20 / 50 / 100 / 200 trend, 1-hour bars: an RSI over 80 with the EMAs stacked up in the last 3 bars goes long, an RSI under 20 with them stacked down goes short; a long closes on an RSI under 30 within 2 bars of the EMA 50 under the EMA 200, a short on the mirror; reversing.
Port of FMZ strategy #458074 "Multi Indicator Trend Following Strategy" (Trendy Strategy).

FMZ source id: 458074

Source
    https://www.fmz.com/strategy/458074 (PineScript v5, FMZ last modified 2024-07-29 17:07:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 187-248), RSI 3, levels 80 / 20; EMA 20 / 50 / 100 / 200; exits RSI 30 / 70 within 2 bars of the EMA 50 / 200 cross state; flags inLong / inShort
    barssince(longSignal) <= 2 and not inLong -> inLong, entry Long;  else barssince(shortSignal) <= 2 and not inShort -> inShort, entry Short
    else inLong and barssince(ema50 < ema200) <= 2 and rsi < 30 -> close Long;  else inShort and barssince(ema50 > ema200) <= 2 and rsi > 70 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The inLong / inShort flags and the else-if chain are followed bar by bar as written; a close acts
      only on a position held into the bar. ta.barssince is na before the first occurrence, so the tests
      fail there. Exits are bar-close tests filled at the next open. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI extremes in a stacked EMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458074_rsi3_extreme_stacked_ema_flags_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [3, 7],
    "long_th": [80, 70],
    "short_th": [20, 30],
}
DEFAULT_PARAMS = {"rsi_len": 3, "long_th": 80, "short_th": 20}


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
    return 100 - 100 / (1 + up / dn)


def _barssince(cond):
    """Pine's ta.barssince: bars since cond was last true (0 on a true bar), na before the first."""
    v = np.asarray(cond, dtype=bool)
    out = np.full(len(v), np.nan)
    last = -1
    for i in range(len(v)):
        if v[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e20, e50, e100, e200 = (c.ewm(span=n, adjust=False).mean() for n in (20, 50, 100, 200))
    r = _rsi(c, int(p["rsi_len"]))
    up = (e20 > e50) & (e50 > e100) & (e100 > e200)
    dn = (e20 < e50) & (e50 < e100) & (e100 < e200)
    with np.errstate(invalid="ignore"):
        lcm = _barssince((r > float(p["long_th"])) & up) <= 2
        scm = _barssince((r < float(p["short_th"])) & dn) <= 2
        lstop = (_barssince(e50 < e200) <= 2) & (r < 30).to_numpy()
        sstop = (_barssince(e50 > e200) <= 2) & (r > 70).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, in_long, in_short = 0, False, False
    for i in range(m):
        cur = pos
        if lcm[i] and not in_long:
            in_long, in_short, cur = True, False, 1
        elif scm[i] and not in_short:
            in_short, in_long, cur = True, False, -1
        elif in_long and lstop[i]:
            in_long = False
            if pos == 1:
                cur = 0
        elif in_short and sstop[i]:
            in_short = False
            if pos == -1:
                cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
