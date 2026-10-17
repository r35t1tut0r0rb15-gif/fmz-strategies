"""SMA 14 / 28 crosses with a money bracket, 10-minute bars: the SMA 14 crossing above the SMA 28 goes long, below goes
short; each position carries a target and a stop of 200 / 100 dollars per contract (price units for one contract),
which become ATR multiples.
Port of FMZ strategy #433010 "Price based Stop Loss and Take Profit Strategy" (Stop loss and Take Profit in $$ example).

FMZ source id: 433010

Source
    https://www.fmz.com/strategy/433010 (PineScript v4, FMZ last modified 2023-11-23 15:36:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 144-157), SMA 14 / 28; take profit 200 $, stop loss 100 $ (one contract, the default quantity)
    crossover(sma(close, 14), sma(close, 28)) -> entry long;  crossunder -> entry short
    exit(profit = money / pointvalue / |position_size| / mintick, loss = the same for 100 $)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: with the default quantity of one contract the dollar amounts are price distances
      (200 / 100 USD on BTC_USDT, about 3.3 / 1.7 ATR of 10-minute BTC, ATR about 60 USD). They become
      tp_atr / sl_atr x Wilder ATR 14 of the signal bar as fractions of its close, shifted one bar
      inside stops() and re-based on the fill (the source measures from the average entry price).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, money (price-unit) distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the money-to-points conversion by position size stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG433010 (2 members, best partner #442933, Jaccard 0.948); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433010_sma_cross_money_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [3.3, 1.5],
    "sl_atr": [1.7, 1.0],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28, "atr_len": 14, "tp_atr": 3.3, "sl_atr": 1.7}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    se = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return le, se, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
