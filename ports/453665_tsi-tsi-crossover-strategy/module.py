"""TSI (8 / 8, signal 3) crossings at extremes inside a 10:00-15:30 New York weekday session, 5-minute bars: a TSI cross up with the signal under -50 goes long, a cross down with the signal over 50 goes short, at least 12 bars after the last entry; the opposite TSI cross closes; reversing.
Port of FMZ strategy #453665 "TSI交叉策略-TSI-Crossover-Strategy" (TSI Entries).

FMZ source id: 453665

Source
    https://www.fmz.com/strategy/453665 (PineScript v5, FMZ last modified 2024-06-07 16:36:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-200), TSI long 8, short 8, signal 3; lines -50 / 50; session 1000-1530 America/New_York, days 2-6 (Mon-Fri); 12 bars between entries
    in session and bar_index - lastEntry > 12:  signal < -50 and crossover(tsi, signal) -> entry Up;  else signal > 50 and crossunder -> entry Down (lastEntry = bar_index)
    long and crossunder -> close Up;  else short and crossover -> close Down

Interpretation choices (Pine rules in SURVEY_README.md)
    * The session is read on the bar's open in America/New_York time, so it follows New York daylight
      saving (the bars are UTC; the conversion is explicit). The entry spacing counts bars from the
      last entry call (also an ignored one). A cross up that enters long while short reverses, and
      the short's close then finds it reversed. qty_percent = 100 closes the whole trade. REVERSAL
      INTENDED. The margin settings are sizing. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TSI extreme crossings in a session.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 10:00-15:30 America/New_York, Monday-Friday, on the bar open.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453665_tsi_extreme_cross_ny_session_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tsi_long": [8, 25],
    "tsi_short": [8, 13],
    "gap_bars": [12, 6],
}
DEFAULT_PARAMS = {"tsi_long": 8, "tsi_short": 8, "signal": 3, "gap_bars": 12, "lower": -50.0, "upper": 50.0,
                  "sess_from": 600, "sess_to": 930}


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
    pc = c.diff()

    def ds(x):
        return x.ewm(span=int(p["tsi_long"]), adjust=False).mean().ewm(span=int(p["tsi_short"]), adjust=False).mean()

    tsi = 100 * ds(pc) / ds(pc.abs())
    sig = tsi.ewm(span=int(p["signal"]), adjust=False).mean()
    co = ((tsi > sig) & (tsi.shift(1) <= sig.shift(1))).to_numpy()
    cu = ((tsi < sig) & (tsi.shift(1) >= sig.shift(1))).to_numpy()
    sv = sig.to_numpy()
    ny = bars_df.index.tz_convert("America/New_York")
    tod = ny.hour * 60 + ny.minute
    sess = ((tod >= int(p["sess_from"])) & (tod < int(p["sess_to"])) & (ny.dayofweek <= 4))
    sess = np.asarray(sess)
    gap = int(p["gap_bars"])
    lo_l, up_l = float(p["lower"]), float(p["upper"])
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, last = 0, None
    for i in range(m):
        cur = pos
        allowed = sess[i] and (last is None or i - last > gap)
        if allowed:
            if sv[i] < lo_l and co[i]:
                if cur != 1:
                    cur = 1
                last = i
            elif sv[i] > up_l and cu[i]:
                if cur != -1:
                    cur = -1
                last = i
        if pos > 0 and cu[i]:
            if cur == 1:
                cur = 0
        elif pos < 0 and co[i]:
            if cur == -1:
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
