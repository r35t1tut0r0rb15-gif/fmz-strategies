"""MACD(12, 26, 9) crossings away from zero with an SMA 200 filter, 1-hour bars: the MACD crossing over its signal with both under zero and the close above the SMA 200 goes long, the mirror short; a 2 %
target and 2 % stop from the fill; reversing.
Port of FMZ strategy #442516 "MACD量化策略之双重叉叉均线突破策略Dual-Moving-Average-Crossover-MACD-Quantitative-Strategy" (Simple MACD strategy).

FMZ source id: 442516

Source
    https://www.fmz.com/strategy/442516 (PineScript v4, FMZ last modified 2024-02-22 15:32:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-191), MACD 12 / 26 / 9 (EMA); SMA 200; take profit 2 % each side, stop 2 %; margin 100
    crossover(macd, signal) and macd < 0 and signal < 0 and close > sma200 -> entry long;  crossunder and both > 0 and close < sma200 -> entry short
    position_size > 0 -> exit(limit = avg (1 + 2 %), stop = avg (1 - 2 %));  position_size < 0 -> exit(limit = avg (1 - 2 %), stop = avg (1 + 2 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent every bar from the average (fill) price at the same levels; on the signal bar
      the position is flat and nothing is sent, so the bracket is ported active from the fill bar
      (#440797): fixed fractions 0.02 / 0.02 of the fill. strategy.entry reverses: REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). The margin settings are sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed from the fill.
    2 generic: PASS, MACD crossings with an SMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin settings stored.
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

NAME = "fmz_442516_macd_cross_zero_side_sma200_pct_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.02, 0.04],
    "ma_len": [200, 100],
}
DEFAULT_PARAMS = {"tp_pct": 0.02, "sl_pct": 0.02, "ma_len": 200, "fast": 12, "slow": 26, "signal": 9}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    ma = c.rolling(int(p["ma_len"])).mean()
    lsig = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (macd < 0) & (sig < 0) & (c > ma)).to_numpy()
    ssig = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & (macd > 0) & (sig > 0) & (c < ma)).to_numpy()
    s_, t_ = float(p["sl_pct"]), float(p["tp_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 < m:
            if lsig[i] and pos != 1:
                le[i], pos, entry_i = True, 1, i + 1
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i = True, -1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
