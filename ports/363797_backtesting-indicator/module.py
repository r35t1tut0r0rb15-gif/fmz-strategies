"""EMA 14/22 cross above EMA 200 goes long; a close-checked trailing stop (armed 0.65 % above the
signal close, trailing 0.3 % under the highest close) or a close 3.5 % under the signal close
goes short (always in after the first long).
Port of FMZ strategy #363797 "Backtesting- Indicator".

Source
    https://www.fmz.com/strategy/363797 (PineScript v5, FMZ last modified 2022-05-17 14:05:42).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 68-216), EMA 14 / 22 / 200, stop 3.5 %, arm 0.65 %,
trail 0.3 %
    buyAlert  = crossover(ema14, ema22) and close > ema200 and lastsignal != 1
    on buyAlert: buy value = close; trigger = value * 1.0065; trail running, not active
    beginTrail: running, not active, close > value * 1.0065 and crossover(close, trigger)
                -> trigger = close, active, stop = close * 0.997
    runTrail:   active and (crossover(close, trigger) or close >= trigger)
                -> trigger = close, stop = close * 0.997
    Sell1 = active and (crossunder(close, stop) or (close[1] > stop and close < stop))
    Sell2 = crossunder(close, value * 0.965)
    sellAlert = (Sell1 or Sell2) and lastsignal != -1 (resets the trail)
    buyAlert -> entry long; else sellAlert -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail and the 3.5 % stop are checked on closes: ported as close-based signals, not
      engine stops (rules 2 and 3, 2026-10-07); the trail carries the mark
      trailing_stop_pending.
    * "Opening balance", "allocated %" and "commission" only feed the script's own table; not
      ported (sizing / costs).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_363797_ema_cross_close_trail"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema1": [9, 14],
    "ema2": [22, 34],
    "stop_loss": [0.02, 0.035],
}
DEFAULT_PARAMS = {"ema1": 14, "ema2": 22, "ema3": 200, "stop_loss": 0.035, "trail_arm": 0.0065,
                  "trail_pct": 0.003}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    cs = bars_df["close"]
    e1, e2, e3 = (cs.ewm(span=int(p[k]), adjust=False).mean() for k in ("ema1", "ema2", "ema3"))
    alert_buy = ((e1 > e2) & (e1.shift(1) <= e2.shift(1)) & (cs > e3)).to_numpy()
    c = cs.to_numpy(dtype=float)
    arm, pct, sl = p["trail_arm"], p["trail_pct"], p["stop_loss"]
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last = 0
    value = trig = stop = low_line = np.nan
    trig_prev = stop_prev = low_prev = np.nan
    active = running = 0
    for i in range(m):
        c1 = c[i - 1] if i else np.nan
        buy = bool(alert_buy[i]) and last != 1
        if buy:
            last = 1
            value = c[i]
        low_line = value - value * sl
        if buy:
            trig = value + value * arm
            active, running = 0, 1
            stop = trig - trig * pct
        if running == 1 and active == 0 and c[i] > value + value * arm and c[i] > trig and c1 <= trig_prev:
            trig, active = c[i], 1
            stop = trig - trig * pct
        if active == 1 and ((c[i] > trig and c1 <= trig_prev) or c[i] >= trig):
            trig = c[i]
            stop = trig - trig * pct
        tsl = active == 1 and ((c[i] < stop and c1 >= stop_prev) or (c1 > stop and c[i] < stop))
        sell2 = c[i] < low_line and c1 >= low_prev
        sell = (tsl or sell2) and last != -1
        if sell:
            last = -1
            active = running = 0
        le[i], se[i] = buy, sell and not buy
        trig_prev, stop_prev, low_prev = trig, stop, low_line
    return _always_in(le, se, bars_df.index)


def portfolio_kwargs(**params):
    return {}
