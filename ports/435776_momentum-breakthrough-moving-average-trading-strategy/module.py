"""Three-minute bars: the close crossing over the EMA 458 on a bar whose volume is above 1.5 x its EMA 21 goes long, crossing under it on such a bar goes short; a 1 % stop and a 2 % target from the entry; reversing.
Port of FMZ strategy #435776 "Momentum Breakthrough Moving Average Trading Strategy" (Di strategy (TradingSignalHub)).

FMZ source id: 435776

Source
    https://www.fmz.com/strategy/435776 (PineScript v5, FMZ last modified 2023-12-18 18:01:59).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 155-231), DI EMA 458; volume EMA 21 x 1.5; SL 1 %, TP 2 %; EMA 34 / 89 bands plots only; window 2023 .. 2033
    EMAbuy = crossover(close, ema(close, 458));  Volhigh = volume > ema(volume, 21) x 1.5;  EMAbuy and Volhigh -> entry Long;  EMAsell and Volhigh -> entry Short
    position_size > 0 -> exit(stop = avg x 0.99, limit = avg x 1.02);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume test compares the bar with its own EMA. The exits are sent once a position exists (from
      the bar after the fill in the script, from the fill in the port). The 2023 .. 2033 window is dropped.
      REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver D4). FREQ = "3min" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, long-EMA crossings on volume spikes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > 1.5 x ema(volume, 21); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 2023 .. 2033 window dropped).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435776_ema458_cross_volume_spike_3m_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [458, 200],
    "vol_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"ema_len": 458, "vol_len": 21, "vol_mult": 1.5, "sl": 0.01, "tp": 0.02}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    vh = v > v.ewm(span=int(p["vol_len"]), adjust=False).mean() * float(p["vol_mult"])
    up = (c > e) & (c.shift(1) <= e.shift(1)) & vh
    dn = (c < e) & (c.shift(1) >= e.shift(1)) & vh
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
