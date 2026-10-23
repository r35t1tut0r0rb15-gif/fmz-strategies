"""Hourly bars: the close crossing over a VWAP cumulated from the first loaded bar goes long, crossing under goes short; a close 3 % beyond the entry takes profit and 1 % against it stops, both at the next open; reversing.
Port of FMZ strategy #437032 "Volume Weighted Average Price Strategy" (VWAP Strategy by Royce Mars).

FMZ source id: 437032

Source
    https://www.fmz.com/strategy/437032 (PineScript v4, FMZ last modified 2023-12-29 16:31:33).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 135-171), cumulative VWAP of hlc3 (the Period input 14 is unused); TP 3 %, SL 1 % (close-based)
    vwapValue = cum(hlc3 x volume) / cum(volume) from the first bar (var sums);  crossover(close, vwap) -> entry Buy;  crossunder -> entry Short
    close Buy when crossunder or close / avg >= 1.03 or close / avg <= 0.99;  close Short when crossover or close / avg <= 0.97 or >= 1.01

Interpretation choices (Pine rules in SURVEY_README.md)
    * The VWAP never resets: it runs from the first loaded bar, so where it sits depends on the data's
      start (weird case). The "Period" input is not used. The take-profit and stop are bar-close tests on
      the average price (the fill), exiting at the next open: ported in the signals. A close acts only on
      a position the bar's entries leave unchanged (call order). REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based target and stop in the signals.
    2 generic: PASS, crossings of a cumulative VWAP.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the cumulative VWAP; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the VWAP is never reset).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437032_cumulative_vwap_cross_close_bracket_reversal"
FAMILY = "vwap_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp": [0.03, 0.05],
    "sl": [0.01, 0.02],
}
DEFAULT_PARAMS = {"tp": 0.03, "sl": 0.01}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    cvol = v.cumsum()
    vwap = ((h + lo + c) / 3 * v).cumsum() / cvol.where(cvol != 0)
    up = ((c > vwap) & (c.shift(1) <= vwap.shift(1))).to_numpy()
    dn = ((c < vwap) & (c.shift(1) >= vwap.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp, sl = float(p["tp"]), float(p["sl"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, avg = 0, 0, np.nan
    for i in range(m):
        if pend != 0:
            pos, avg, pend = pend, ov[i], 0
        if up[i] and pos != 1 and i + 1 < m:
            le[i], pend = True, 1
            continue
        if dn[i] and pos != -1 and i + 1 < m:
            se[i], pend = True, -1
            continue
        r = cv[i] / avg if pos != 0 else np.nan
        if pos == 1 and (r >= 1 + tp or r <= 1 - sl):
            lx[i], pos = True, 0
        elif pos == -1 and (r <= 1 - tp or r >= 1 + sl):
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
