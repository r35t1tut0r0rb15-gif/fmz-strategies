"""EMA 14 / 22 crossings above the EMA 200 with a close-based percent trailing exit, 1-hour bars, long only: a fast crossing over the slow EMA with the close above the EMA 200 buys (once per sell); the trail arms
when a close passes 0.65 % above the buy close, then follows each new high close and sells on a close 0.3 % under it; a close crossing under 3.5 % below the buy close also sells.
Port of FMZ strategy #436984 "Dynamic Trailing Stop Loss Strategy" (PCT Trailing Stoploss- Strategy).

FMZ source id: 436984

Source
    https://www.fmz.com/strategy/436984 (PineScript v5, FMZ last modified 2023-12-29 10:42:27).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 164-305), stop 3.5 %, trail arm 0.65 %, trail 0.3 %; EMA 14 / 22 / 200
    alertBuy = crossover(ema 14, ema 22) and close > ema 200;  buyAlert = alertBuy and lastsignal != 1;  alertBuyValue = valuewhen(buyAlert, close, 0);  stop line = buy value x (1 - 0.035)
    trail: armed by crossover(close, buy value x 1.0065) above it, then TSLTriggerValue := close on each new high close, TSLStop = trigger x (1 - 0.003);  sell = crossunder(close, TSLStop) or crossunder(close, stop line), once per buy;  buyAlert -> entry Buy;  sellAlert -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is tested on bar closes (crossunder of the close), so it is a close-based exit signal from
      simulate(), not a stop (SURVEY_README rule 2); no mark. The percent distances are kept as percents
      of the buy close (the script's own normalisation). lastsignal alternates buy and sell signals as
      written; each crossover / crossunder compares with the level's value at the previous bar's end. Long
      only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; trail and stop tested on closes.
    2 generic: PASS, percent distances from the buy close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND363797 (2 members, best partner #363797, Jaccard 0.794); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436984_ema_cross_close_trail_long"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trail_pct": [0.003, 0.01],
    "stop_pct": [0.035, 0.02],
}
DEFAULT_PARAMS = {"trail_pct": 0.003, "stop_pct": 0.035, "arm_pct": 0.0065, "ema1": 14, "ema2": 22, "ema3": 200}


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
    e1, e2, e3 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("ema1", "ema2", "ema3"))
    alert_buy = ((e1 > e2) & (e1.shift(1) <= e2.shift(1)) & (c > e3)).to_numpy()
    cv = c.to_numpy(dtype=float)
    arm, tpct, spct = float(p["arm_pct"]), float(p["trail_pct"]), float(p["stop_pct"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last = 0
    active = running = 0
    trig = stop = 0.0
    buy_v = np.nan
    trig_p = stop_p = 0.0                   # values at the previous bar's end (for crossover [1])
    low_p = np.nan
    for i in range(m):
        ci = cv[i]
        c1 = cv[i - 1] if i >= 1 else np.nan
        buy = bool(alert_buy[i]) and last != 1
        if buy:
            last = 1
            buy_v = ci
        low_v = buy_v - buy_v * spct
        if buy:
            trig = buy_v + buy_v * arm
            active, running = 0, 1
            stop = trig - trig * tpct
        begin = (running == 1 and active == 0 and ci > buy_v + buy_v * arm and ci > trig and c1 <= trig_p)
        if begin:
            trig, active = ci, 1
            stop = trig - trig * tpct
        run = active == 1 and ((ci > trig and c1 <= trig_p) or ci >= trig)
        if run:
            trig = ci
            stop = trig - trig * tpct
        tsl = active == 1 and ((ci < stop and c1 >= stop_p) or (c1 > stop and ci < stop))
        sell2 = ci < low_v and c1 >= low_p
        sell = (tsl or sell2) and last != -1
        if sell:
            last = -1
            active = running = 0
        if buy:
            le[i] = True
        if sell:
            lx[i] = True
        trig_p, stop_p, low_p = trig, stop, low_v
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
