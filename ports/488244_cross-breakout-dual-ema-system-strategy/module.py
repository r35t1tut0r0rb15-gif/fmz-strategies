"""EMA 32 high / low channel breakouts confirmed by the first clean candle, 1-hour bars: after the close crosses above the
EMA 32 of highs, the first green candle whose low stays above that EMA marks a high; the bar after one that breaks
that high, a green candle goes long; the trade closes when the close falls below the EMA 32 of lows; shorts mirror it.
Port of FMZ strategy #488244 "交叉突破型双均线系统策略-Cross-Breakout-Dual-EMA-System-Strategy" (TrophyFighter 32 EMA HL).

FMZ source id: 488244

Source
    https://www.fmz.com/strategy/488244 (PineScript v5, FMZ last modified 2025-03-26 11:14:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 148-247), EMA 32 of high and of low
    crossover(close, emaH) and not in a trade -> waiting_for_long, first_green_high = na
    green and low > emaH and waiting and the last cross is after the previous such candle -> first_green_high = high
    long_breakout_check = high > first_green_high and waiting;  long = long_breakout_check[1] and green and not in a trade
    long -> waiting off, in_long_trade;  close < emaL and in_long_trade -> in_long_trade off, close long (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.valuewhen(cross, bar_index, 0) > ta.valuewhen(clean candle, bar_index, 1): the candle is the first clean one
      since the last cross (na before two clean candles exist: false).
    * The script's own in-trade flags gate the entries; the Pine position follows strategy.entry / strategy.close:
      closes act on the position held at the bar's start and never undo an entry on that bar (#430850); a short entry
      while long (possible only after the flags were cleared) reverses it. REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs of highs and lows and candle colours.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488244_ema32_hl_clean_candle_breakout"
FAMILY = "ma_channel_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [32, 50],
}
DEFAULT_PARAMS = {"ema_len": 32}


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
    n = int(p["ema_len"])
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    eh, el = h.ewm(span=n, adjust=False).mean(), lo.ewm(span=n, adjust=False).mean()
    x_up = ((c > eh) & (c.shift(1) <= eh.shift(1))).to_numpy()
    x_dn = ((c < el) & (c.shift(1) >= el.shift(1))).to_numpy()
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    ntg = ((c > o) & (lo > eh)).to_numpy()
    ntr = ((c < o) & (h < el)).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    ehv, elv = eh.to_numpy(dtype=float), el.to_numpy(dtype=float)
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    fgh = frl = np.nan
    wait_l = wait_s = in_l = in_s = False
    last_xu = last_xd = None                        # valuewhen(cross, bar_index, 0)
    last_ntg = last_ntr = None                      # latest clean candle before the current bar
    prev_lchk = prev_schk = False
    pos = 0
    for i in range(m):
        if x_up[i]:
            last_xu = i
        if x_dn[i]:
            last_xd = i
        if x_up[i] and not in_l and not in_s:
            fgh, wait_l = np.nan, True
        if x_dn[i] and not in_l and not in_s:
            frl, wait_s = np.nan, True
        if ntg[i] and wait_l and last_xu is not None and last_ntg is not None and last_xu > last_ntg:
            fgh = hv[i]
        if ntr[i] and wait_s and last_xd is not None and last_ntr is not None and last_xd > last_ntr:
            frl = lv[i]
        if ntg[i]:
            last_ntg = i
        if ntr[i]:
            last_ntr = i
        lchk = (not np.isnan(fgh)) and hv[i] > fgh and wait_l
        schk = (not np.isnan(frl)) and lv[i] < frl and wait_s
        long_c = prev_lchk and green[i] and not in_l and not in_s
        short_c = prev_schk and red[i] and not in_l and not in_s
        prev_lchk, prev_schk = lchk, schk
        if long_c:
            wait_l, in_l = False, True
        if short_c:
            wait_s, in_s = False, True
        long_x = cv[i] < elv[i] and in_l
        short_x = cv[i] > ehv[i] and in_s
        if long_x:
            in_l = False
        if short_x:
            in_s = False
        start = pos
        if long_c:
            pos = 1
        if short_c:
            pos = -1
        if long_x and start == 1 and pos == 1:
            pos = 0
        if short_x and start == -1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
