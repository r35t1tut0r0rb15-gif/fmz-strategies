"""Pullback buying with a lower-close exit, 1-hour bars, long only: when flat, buy a close over the 200 average but under the 10 average, or any close more than 14 % under the 52-bar high; sell a close over the 10
average that is also under the previous low; a close more than 15 % under the buy price (measured on the close) also sells.
Port of FMZ strategy #436500 "Dual Moving Average Reversal Strategy" (Davin's 10/200MA Pullback on SPY Strategy v2.0).

FMZ source id: 436500

Source
    https://www.fmz.com/strategy/436500 (PineScript v5, FMZ last modified 2023-12-25 13:24:14).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 155-222), MA 200 / 10 / 50, stop 0.15, exit on lower close, buy the dip trigger 14 %
    buyCondition = flat and ((close > ma200 and close < ma10) or (dip and (highest(high, 52) - close) / highest(high, 52) 100 > 14));  sellCondition = long and close > ma10 and close < low[1]
    stopDistance = (buyPrice - close) / close;  stopCondition = long and stopDistance > 0.15 (or, off, ma50 < ma200);  entry Long when buyCondition;  buyPrice := open on the bar after a buy;  close when sell or stop

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is a test on each bar's CLOSE against the buy price (the fill bar's open), so it is an exit
      signal filled at the next open, not a bracket. The distance is measured against the current close
      as written. The buy price on the fill bar still holds the earlier value (na after an exit, 0 at
      the start), so no stop can fire on the fill bar. The crossover stop input is off by default and is
      kept as a fixed switch. Long only. The percent-of-equity size is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, stop is a close test, a fraction of the buy price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the stop percent stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436500_ma_pullback_dip_buyer"
FAMILY = "mean_reversion"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma2": [10, 20],
    "trigger": [14, 20],
    "stop_pct": [0.15, 0.10],
}
DEFAULT_PARAMS = {"ma1": 200, "ma2": 10, "ma3": 50, "stop_pct": 0.15, "lower_close": True,
                  "dip": True, "trigger": 14, "by_cross": False}


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
    ma1 = c.rolling(int(p["ma1"])).mean().to_numpy()
    ma2 = c.rolling(int(p["ma2"])).mean().to_numpy()
    ma3 = c.rolling(int(p["ma3"])).mean().to_numpy()
    hh = h.rolling(52).max()
    chg = ((hh - c) / hh * 100.0).to_numpy()
    cc, oo, low1 = c.to_numpy(), o.to_numpy(), lo.shift(1).to_numpy()
    m = len(cc)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    bp = 0.0
    prev_buy = False
    op = None
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if i > 0 and op is not None:          # fills at this bar's open
                if op == "eL" and pos == 0:
                    pos = 1
                elif op == "X" and pos > 0:
                    pos = 0
            held[i] = pos
            op = None
            bp_start = bp
            buy = pos == 0 and ((cc[i] > ma1[i] and cc[i] < ma2[i])
                                or (bool(p["dip"]) and chg[i] > float(p["trigger"])))
            sell = pos > 0 and cc[i] > ma2[i] and ((cc[i] < low1[i]) if p["lower_close"] else True)
            dist = (bp_start - cc[i]) / cc[i] if pos > 0 else np.nan
            stop = pos > 0 and ((dist > float(p["stop_pct"])) or (bool(p["by_cross"]) and ma3[i] < ma1[i]))
            if buy:
                op = "eL"
            if prev_buy:
                bp = oo[i]
            if sell or stop:
                op = "X"
                bp = np.nan
            prev_buy = bool(buy)
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
