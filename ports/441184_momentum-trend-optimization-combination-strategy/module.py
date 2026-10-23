"""Hourly bars, long only: the EMA 2 crossing over a slope-adjusted SMA 8 line with the close above the SMA 35, volume above its EMA 20 and the SMA 50 rising over 4 bars goes long; the next time the EMA 2 crosses over that line again it closes; a 50 % stop and a 25 % target from the entry.
Port of FMZ strategy #441184 "Momentum Trend Optimization Combination Strategy" (Optimized Zhaocaijinbao (fzj20020403)).

FMZ source id: 441184

Source
    https://www.fmz.com/strategy/441184 (PineScript v5, FMZ last modified 2024-02-06 15:11:57).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 127-189), SMA 6 / 35; buy line EMA 2; sell line SMA 8 + 8-bar slope; volume EMA 20; SMA 50 slope over 4 bars; stop 50 %, target 25 %
    buySignal = crossover(buyLine, sellLine) and close > ma35 and volume > ema(volume, 20) and weeklySlope;  sellSignal = crossunder(sellLine, buyLine)
    buySignal and not inPosition -> entry Long, inPosition := true;  sellSignal and inPosition -> close Long, inPosition := false;  if inPosition: exit(stop = avg x 0.5), exit(limit = avg x 1.25)

Interpretation choices (Pine rules in SURVEY_README.md)
    * crossunder(sellLine, buyLine) is the same event as crossover(buyLine, sellLine), so a long opened
      on one upward cross is closed on the next one (weird case). inPosition is the script's own flag: it
      stays true after the stop or target closes the trade, so no new entry comes until the next cross
      clears it, as written. The stop and target are levels from the average (fill) price, re-sent with
      the same values: a fixed sl_stop 0.5 / tp_stop 0.25 of the fill. Long only. The ATR position size
      is sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed stop and target from the fill.
    2 generic: PASS, fast EMA crossings of a slope-adjusted SMA with trend and volume filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x 1 % x 2 / ATR, 100 % of equity default, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its EMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441184_ema2_slope_sma8_cross_volume_trend_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_len": [35, 50],
    "tp": [0.25, 0.1],
}
DEFAULT_PARAMS = {"ma_len": 35, "sl": 0.5, "tp": 0.25}


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
    c, v = bars_df["close"], bars_df["volume"]
    buy_l = c.ewm(span=2, adjust=False).mean()
    sell_l = (c - c.shift(8)) / 8 + c.rolling(8).mean()
    cross = ((buy_l > sell_l) & (buy_l.shift(1) <= sell_l.shift(1))).to_numpy()
    w = c.rolling(50).mean()
    filt = ((c > c.rolling(int(p["ma_len"])).mean()) & (v > v.ewm(span=20, adjust=False).mean())
            & ((w - w.shift(4)) / 4 > 0)).to_numpy()
    m = len(cross)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    flag = False
    for i in range(m):
        buy_c = cross[i] and filt[i] and not flag      # both read the flag of the previous bar
        sell_c = cross[i] and flag
        if buy_c:
            le[i], flag = True, True
        elif sell_c:
            lx[i], flag = True, False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
