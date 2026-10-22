"""5 EMA alert-candle breaks, 15-minute bars: a bar breaking under the low of a previous bar that sat wholly above the EMA 5 goes short (only while no short setup is armed); a bar breaking over the high of a
previous bar wholly under the EMA 5 goes long; reversing; the written stop / target closes name ids that are never entered.
Port of FMZ strategy #440057 "Momentum Pullback Strategy" (Ultimate 5EMA Strategy By PowerOfStocks).

FMZ source id: 440057

Source
    https://www.fmz.com/strategy/440057 (PineScript v5, FMZ last modified 2024-01-26 11:07:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-279), extra SL off (5); risk : reward 3; show sell on, show buy off; candle-close condition off
    Short = low[1] > ema5[1] and low[1] > low and shortC == 0;  shortC counts armed setups, reset by sslhit (high > high[1] of the setup) or starhit (low < target);  Long = high[1] < ema5[1] and high[1] < high and longC == 0
    entry Buy when Long;  entry Sell when Short;  close("ExitBuy") / close("ExitSell") on the hits  -- no such entry ids

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short setup counter is armed only with "show sell" (on) and cleared when the setup's stop or
      target is touched, so a new short waits for that. The long counter needs "show buy" (off) and
      stays 0, so every long setup sends the entry, as written. The two closes name ids that are never
      entered and do nothing; positions change only by reversal (the intended exits are owed). The two
      setups cannot share a bar. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ =
      "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA alert-candle breaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440057_power_of_stocks_5ema_breaks"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [5, 9],
    "rire": [3, 2],
}
DEFAULT_PARAMS = {"ema_len": 5, "rire": 3}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    rr = float(p["rire"])
    m = len(hv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sc, slc, stc = 0, 0, 0
    ssl, star = np.nan, np.nan
    for i in range(1, m):
        short_ = lv[i - 1] > e[i - 1] and lv[i - 1] > lv[i] and sc == 0
        sslhit = hv[i] > ssl and sc > 0 and slc == 0
        starhit = lv[i] < star and sc > 0 and stc == 0
        long_ = hv[i - 1] < e[i - 1] and hv[i - 1] < hv[i]
        if short_:
            sc, slc, stc = sc + 1, 0, 0
            ssl = hv[i - 1]
            star = lv[i - 1] - (hv[i - 1] - lv[i - 1]) * rr
        if not sslhit and not starhit and sc > 0:
            slc, stc = 0, 0
        elif sslhit:
            sc, slc = 0, slc + 1
        elif starhit:
            sc, stc = 0, stc + 1
        le[i], se[i] = long_, short_
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
