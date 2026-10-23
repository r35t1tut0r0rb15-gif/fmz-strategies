"""Hourly bars: the SMA 7 crossing over the SMA 25 on volume above its 20-bar average goes long, crossing under on volume BELOW its average goes short; each trade gets a 1 % stop and a 2 % target from the signal close and closes 50 bars after its signal; reversing.
Port of FMZ strategy #458238 "SMA交叉与成交量过滤的自适应动态止盈止损策略Adaptive-Dynamic-Stop-Loss-and-Take-Profit-Strategy-with-SMA-Crossover-and-Volume-Filter" (Simple_CrossOver_Bot_V1_EBO).

FMZ source id: 458238

Source
    https://www.fmz.com/strategy/458238 (PineScript v5, FMZ last modified 2024-07-31 11:20:39).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 215-285), SMA 7 / 25; volume SMA 20; SL 1 %, TP 2 % from the signal close; max 50 bars
    LONG = crossover(fast, slow) and fast > slow and volume > volume_SMA -> entry LONG, exit(stop = close x 0.99, limit = close x 1.02), long_entry_bar_index := bar_index
    SHORT = crossunder(fast, slow) and fast < slow and volume < volume_SMA -> entry SHORT, exit(stop = close x 1.01, limit = close x 0.98)
    bar_index - long_entry_bar_index >= 50 -> close LONG, index := na  (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent only on signal bars, as levels from that close: ported as fractions of the
      fill, exact (1e-6 floor). The time close is sent on the 50th bar after the signal bar and fills at
      the next open; it is only acted on while that side is held, and a new same-side signal restarts it
      (a repeated signal while in the position also re-sends the bracket from the new close: not
      followed). The short needs volume under its average (as written; the long needs it above). The
      date window inputs are unused (timecondition = true). REVERSAL INTENDED. No sizing code. Stop
      module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket at the signal close as fractions of the fill; 50-bar time exit.
    2 generic: PASS, SMA 7 / 25 crossings with volume filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458238_sma7_25_cross_volume_1_2pct_bracket_50bar_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.01, 0.015],
    "tp": [0.02, 0.03],
}
DEFAULT_PARAMS = {"fast": 7, "slow": 25, "vol_len": 20, "sl": 0.01, "tp": 0.02, "max_bars": 50}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    va = v.rolling(int(p["vol_len"])).mean()
    buy = ((f > s) & (f.shift(1) <= s.shift(1)) & (v > va)).to_numpy()
    sell = ((f < s) & (f.shift(1) >= s.shift(1)) & (v < va)).to_numpy()
    k = int(p["max_bars"])
    m = len(buy)
    lx, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    li = si = None
    for i in range(m):
        if buy[i]:
            li = i
        if sell[i]:
            si = i
        if li is not None and i - li >= k:
            lx[i], li = not sell[i], None
        if si is not None and i - si >= k:
            sx[i], si = not buy[i], None
    ix = bars_df.index
    return (pd.Series(buy, index=ix), pd.Series(lx, index=ix),
            pd.Series(sell, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o
    sl, tp = float(p["sl"]), float(p["tp"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - k * (1 - sl))
            .mask(sf, k * (1 + sl) - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, k * (1 + tp) - 1)
            .mask(sf, 1 - k * (1 - tp)))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
