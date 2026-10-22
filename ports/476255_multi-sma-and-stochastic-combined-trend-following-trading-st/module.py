"""Close crossings of the SMA 74 in the outer quarters of the 20-bar range, 4-hour bars: the cross up above the 75 % level goes long, the cross down below the 25 % level goes short; a bar-close test of the low (high) against a hard stop 50 price units from the signal close closes, and so does any bar in a three-candle colour run (the stop moves to that bar's low or high); reversing.
Port of FMZ strategy #476255 "Multi SMA and Stochastic Combined Trend Following Trading Strategy" (Purple SMA Strategy).

FMZ source id: 476255

Source
    https://www.fmz.com/strategy/476255 (PineScript v5, FMZ last modified 2024-12-27 14:43:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-238), zone length 20; SMA 74 (SMA 19 and stochastic 60 / 10 colour the plot only); hard stop 50 ticks x tick size 1.0
    buy = crossover(close, sma74) and close > l + 0.75 (h - l) -> entry Long, stop := close - 50 x 1.0, xMode := false;  sell = crossunder and close < l + 0.25 (h - l) -> entry Short, stop := close + 50, xMode := false
    three green (red) candles -> green (red) run; a red (green) candle in a green (red) run ends it;  in a position and in a run -> xMode := true, stop := low (long) / high (short)
    long: low <= stop -> close Long, else xMode and no run -> close Long;  short: high >= stop -> close Short, else the same

Interpretation choices (Pine rules in SURVEY_README.md)
    * The orders are bar-close tests, filled at the next open, so a loop follows them as written: the
      stop is set on every signal bar (also a repeat signal while held), the run update moves it to the
      CURRENT bar's low (high), so the exit test on that bar always holds and a run closes the position at
      once. A close acts only on the held position and leaves a same-bar reversal standing (as #441963);
      the stop level then carries into the new position as written. The 50-unit stop is a price amount,
      ported as a fraction of 42000 of the signal close. REVERSAL INTENDED. No sizing code. FREQ = "4h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings in the range's outer quarters with candle-run exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_476255_sma74_cross_zone_quarter_candle_run_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "zone_length": [20, 50],
    "sma_length": [74, 50],
}
DEFAULT_PARAMS = {"zone_length": 20, "sma_length": 74, "stop_frac": 1.19048e-03}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["zone_length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    lvl4 = ll + (hh - ll) * 0.75
    lvl2 = ll + (hh - ll) * 0.25
    sma = c.rolling(int(p["sma_length"])).mean()
    buy = ((c > sma) & (c.shift(1) <= sma.shift(1)) & (c > lvl4)).to_numpy()
    sell = ((c < sma) & (c.shift(1) >= sma.shift(1)) & (c < lvl2)).to_numpy()
    grn = (c > o).to_numpy()
    red = (c < o).to_numpy()
    g3 = grn & np.roll(grn, 1) & np.roll(grn, 2)
    r3 = red & np.roll(red, 1) & np.roll(red, 2)
    g3[:2] = False
    r3[:2] = False
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    d = float(p["stop_frac"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    g_run = r_run = xmode = False
    stop = np.nan
    for i in range(m):
        pos = nxt
        if g3[i]:
            g_run, r_run = True, False
        if r3[i]:
            r_run, g_run = True, False
        if (g_run and red[i]) or (r_run and grn[i]):
            g_run = r_run = False
        if buy[i]:
            stop, xmode = cv[i] * (1 - d), False
            if pos != 1:
                le[i], nxt = True, 1
        if sell[i]:
            stop, xmode = cv[i] * (1 + d), False
            if pos != -1:
                se[i], nxt = True, -1
        run = g_run or r_run
        if pos != 0 and run:
            xmode = True
            stop = lv[i] if pos > 0 else hv[i]
        if pos > 0 and not se[i] and (lv[i] <= stop or (xmode and not run)):
            lx[i], nxt = True, 0
        if pos < 0 and not le[i] and (hv[i] >= stop or (xmode and not run)):
            sx[i], nxt = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
