"""MACD crossings outside the Bollinger bands, 1-hour bars: a MACD crossing over its signal with the close above the upper band goes long unless a sell setup came after the last buy setup, the mirror goes short;
reversing; the author's bracket is re-placed every bar at the latest close +60 / -30 points and is described, not emitted.
Port of FMZ strategy #437036 "双均线布林带MACD交易策略Dual-Moving-Average-Bollinger-Band-MACD-Trading-Strategy" (Mod_MACD_BB).

FMZ source id: 437036

Source
    https://www.fmz.com/strategy/437036 (PineScript v4, FMZ last modified 2023-12-29 16:43:01).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 178-223), MACD 12 / 26 / 9, BB 20 x 2, target 60 / stop 30 points
    buy = crossover(macd, signal) and close > upper;  sell = crossunder(macd, signal) and close < lower;  flags open_buy / open_sell set by the setups, reset by the opposite setup (after the entries)
    entry Buy when buy and not open_sell;  entry Sell when sell and not open_buy;  exit(limit = close +- 60, stop = close -+ 30) re-sent EVERY bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags start na; na is read as false (the author's evident meaning), so an entry is blocked only
      while the opposite setup has come since the last same-side setup. The bracket is re-sent on every bar
      from that bar's close, so its levels move after entry (a stop / target 30 / 60 points from the
      latest close, active for the next bar): stops() cannot express a level re-set every bar, so it is
      described here and kept pending (rule 2, mark trailing_stop_pending; points -> ATR multiples when it is
      expressed: about 30 / 60 points against a 1-hour BTC ATR near 150, 0.2 / 0.4 ATR). Positions end at the
      opposite entry until then. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, point bracket described as ATR multiples (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the point inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_437036_macd_cross_outside_bands"
FAMILY = "macd_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "bb_length": [20, 30],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "bb_length": 20, "bb_mult": 2.0}


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
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    buy = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (c > basis + dev)).to_numpy()
    sell = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & (c < basis - dev)).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ob = osl = False
    for i in range(m):
        if buy[i]:
            ob = True
        if sell[i]:
            osl = True
        if buy[i] and not osl:
            le[i] = True
        if sell[i] and not ob:
            se[i] = True
        if sell[i]:
            ob = False
        if buy[i]:
            osl = False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
