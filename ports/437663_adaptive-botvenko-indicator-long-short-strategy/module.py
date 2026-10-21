"""Botvenko log-return levels with an EMA-stack filter, 1-minute bars: the 60-bar log return crossing over 0 (stack up or mixed) goes long, crossing under 0.0065 (stack down or mixed) goes short, with retry
entries at -0.493 / 1.26 and deadline closes at 2 / -1.5 (longs) and -5 (shorts), each order id closing only its own position; reversing.
Port of FMZ strategy #437663 "Adaptive Botvenko Indicator Long Short Strategy" (Boftei's Strategy).

FMZ source id: 437663

Source
    https://www.fmz.com/strategy/437663 (PineScript v5, FMZ last modified 2024-01-04 16:09:30).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 136-247), histogram period 60; levels: buy 0, sell 0.0065, long retry -0.493, long close 2 / -1.5, short retry 1.26, short close -5; EMA 21 / 55 / 89 / 144 stack; direction all; pyramiding 1
    y = log(close) - log(close[60]);  co = crossover(y, 0), cu = crossunder(y, 0.0065), retry / deadline crossings of their levels;  long_st / short_st = EMA 21 > 55 > 89 > 144 / the reverse
    co and (long_st or mixed): close OH BRO, OH DUDE, entry OH DAMN;  retry_long: close OH DAMN, entry OH BRUH;  cu and (short_st or mixed): close OH DAMN, OH BRUH, entry OH BRO;  retry_short: close OH BRO, entry OH DUDE;  deadlines / stack flips close OH DAMN or OH BRO

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are log returns (dimensionless). Each strategy.close names one entry id and only acts
      when that id is the position open at the bar's close; with pyramiding 1 a second same-side id cannot
      add. Orders follow the script's call order, so a close followed by the next id's entry re-enters.
      The date window covers everything: dropped. REVERSAL INTENDED. The 100 % of equity size and margins
      are sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, log-return levels and EMA order.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, margins and pyramiding stored.
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

NAME = "fmz_437663_botvenko_log_return_levels"
FAMILY = "momentum_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "nn": [60, 120],
    "sell": [0.0065, 0.02],
}
DEFAULT_PARAMS = {"nn": 60, "sell": 0.0065, "buy": 0.0, "long1": -0.493, "long2": 2.0, "long3": -1.5,
                  "short1": 1.26, "short2": -5.0}


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
    c = bars_df["close"]
    y = np.log(c) - np.log(c.shift(int(p["nn"])))
    y1 = y.shift(1)

    def xo(lv):
        return ((y > lv) & (y1 <= lv)).to_numpy()

    def xu(lv):
        return ((y < lv) & (y1 >= lv)).to_numpy()

    co, cu = xo(float(p["buy"])), xu(float(p["sell"]))
    rl, dlu, dld = xu(float(p["long1"])), xo(float(p["long2"])), xu(float(p["long3"]))
    rs, ds = xo(float(p["short1"])), xu(float(p["short2"]))
    e = [c.ewm(span=n, adjust=False).mean() for n in (21, 55, 89, 144)]
    ls = ((e[0] > e[1]) & (e[1] > e[2]) & (e[2] > e[3])).to_numpy()
    ss = ((e[0] < e[1]) & (e[1] < e[2]) & (e[2] < e[3])).to_numpy()
    mixed = ~ls & ~ss
    lok, sok = ls | mixed, ss | mixed
    seq = [("close", "OH BRO", co & lok), ("close", "OH DUDE", co & lok), ("entry", "OH DAMN", 1, co & lok),
           ("close", "OH DAMN", rl & lok), ("entry", "OH BRUH", 1, rl & lok),
           ("close", "OH DAMN", cu & sok), ("close", "OH BRUH", cu & sok), ("entry", "OH BRO", -1, cu & sok),
           ("close", "OH BRO", rs & sok), ("entry", "OH DUDE", -1, rs & sok),
           ("close", "OH DAMN", dlu | ss), ("close", "OH DAMN", dld), ("close", "OH BRO", ds | ls)]
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    side, oid = 0, None
    for t in range(m):
        calc_id = oid
        s, oo = side, oid
        for item in seq:
            if item[0] == "entry":
                _, eid, d, cond = item
                if cond[t] and s != d:
                    s, oo = d, eid
            else:
                _, eid, cond = item
                if cond[t] and calc_id == eid and oo == eid:
                    s, oo = 0, None
        if s == 1 and side != 1:
            le[t] = True
        elif s == -1 and side != -1:
            se[t] = True
        elif s == 0 and side == 1:
            lx[t] = True
        elif s == 0 and side == -1:
            sx[t] = True
        side, oid = s, oo
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
