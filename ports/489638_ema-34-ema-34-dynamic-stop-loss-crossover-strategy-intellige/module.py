"""EMA 34 cross-ups with a previous-low stop, a 10 R target and a break-even move at 3 R, checked on bar ranges,
long only, hourly bars: the close crossing above EMA 34 starts a trade (when none is being managed) with the stop at
the previous bar's low; once a close reaches 3 R the stop moves to the entry; a bar whose low reaches the stop or
whose high reaches the target closes the trade at the next open.
Port of FMZ strategy #489638 "EMA-34-动态止损交叉策略趋势跟踪与风险管理的智能结合-EMA-34-Dynamic-Stop-Loss-Crossover-Strategy-Intelligent-Combination-of-Trend-Following-and-Risk-Management" (EMA 34 Crossover with Break Even Stop Loss).

FMZ source id: 489638

Source
    https://www.fmz.com/strategy/489638 (PineScript v5, FMZ last modified 2025-04-07 11:39:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 189-224), EMA 34, RR 10, break-even at 3 R
    long = close > ema34 and close[1] <= ema34[1]
    long and not inTrade -> entryPrice = close, stop = low[1], risk = entry - stop, target = entry + 10 risk,
    entry long, inTrade = true
    inTrade and close >= entry + 3 risk -> stop = entry
    inTrade: low <= stop -> close, inTrade = false;  high >= target -> close, inTrade = false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop and target are tested on the completed bar's low / high and closed with strategy.close: close-checked
      exit signals filled at the next open (rule 3), not stops.
    * The script's own inTrade flag is kept apart from the real position: the checks also run on the signal bar
      itself (before the fill), where a close does nothing but clears inTrade; the entry then still fills and that
      position is unmanaged until the next cross restarts the management, as written. A risk <= 0 (the previous low at
      or above the close) gives a target at or below the entry, which the next check closes, as written.
    * Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and range-checked exits at the next open.
    2 generic: PASS, an EMA and bar levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_489638_ema34_cross_prev_low_stop_10r_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rr": [10.0, 3.0],
    "be_r": [3.0, 1.0],
}
DEFAULT_PARAMS = {"ema_len": 34, "rr": 10.0, "be_r": 3.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    cross = ((c > ema) & (c.shift(1) <= ema.shift(1))).to_numpy()
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_in, pend_out = 0, False, False
    in_trade = False
    entry = stop = target = risk = np.nan
    for i in range(m):
        if pend_in:
            pos, pend_in = 1, False
        if pend_out:
            pos, pend_out = 0, False
        if cross[i] and not in_trade and i >= 1:
            entry, stop = cv[i], lv[i - 1]
            risk = entry - stop
            target = entry + risk * p["rr"]
            if pos == 0 and not pend_in:
                le[i], pend_in = True, True
            in_trade = True
        if in_trade and cv[i] >= entry + risk * p["be_r"]:
            stop = entry
        if in_trade:
            hit_stop = lv[i] <= stop
            hit_tp = hv[i] >= target
            if hit_stop or hit_tp:
                in_trade = False
                if pos == 1 and not pend_out:
                    lx[i], pend_out = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
