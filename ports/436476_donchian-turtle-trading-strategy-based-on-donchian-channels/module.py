"""Donchian breakouts in an EMA 50 / 125 trend, 1-hour bars: a close at or over the previous 20-bar high with the EMA 50 over the EMA 125 goes long (closed under the previous 10-bar low); at or under
the previous 20-bar low with the EMA 50 under the EMA 125 goes short (closed over the previous 10-bar high); each trade has a 2 ATR stop.
Port of FMZ strategy #436476 "基于Donchian通道的海龟交易策略Turtle-Trading-Strategy-Based-on-Donchian-Channels" (Donchian strategy with filter).

FMZ source id: 436476

Source
    https://www.fmz.com/strategy/436476 (PineScript v2, FMZ last modified 2023-12-25 10:57:52).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 161-221), Donchian 20 / 10; EMA 50 / 125; ATR 20 x 2 stop; pyramiding 5, 4 % of equity
    long = close >= highest(20)[1] and ema50 > ema125;  long_exit = close < lowest(10)[1];  short = close <= lowest(20)[1] and ema50 < ema125;  short_exit = close > highest(10)[1]
    entry / close by id;  exit(stop = avg -+ 2 atr(20))

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest() / lowest() read the highs / lows; the entry channel is the previous bar's. The stop is a
      distance of 2 ATR from the average price (re-evaluated each bar with the current ATR in the
      script): ported as sl_stop = 2 x ATR / close of the signal bar, shifted one bar inside stops()
      (re-based on the fill). The extra entries (pyramiding 5) and the percent-of-equity size are sizing.
      The date window is the author's: dropped. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 1-hour bars: not coarse. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: REVIEW, stop distance re-evaluated each bar in the script: fixed at the fill.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and pyramiding stored.
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

NAME = "fmz_436476_donchian_ema_filter_atr_stop"
FAMILY = "breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "donchian_slow": [20, 40],
    "atr_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"donchian_slow": 20, "donchian_fast": 10, "slow_ema": 125, "fast_ema": 50, "atr_len": 20, "atr_mult": 2.0}


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
    n_s, n_f = int(p["donchian_slow"]), int(p["donchian_fast"])
    upper, lower = h.rolling(n_s).max().shift(1), lo.rolling(n_s).min().shift(1)
    upper_f, lower_f = h.rolling(n_f).max().shift(1), lo.rolling(n_f).min().shift(1)
    ema_s = c.ewm(span=int(p["slow_ema"]), adjust=False).mean()
    ema_f = c.ewm(span=int(p["fast_ema"]), adjust=False).mean()
    le = ((c >= upper) & (ema_f > ema_s)).fillna(False)
    lx = (c < lower_f).fillna(False)
    se = ((c <= lower) & (ema_f < ema_s)).fillna(False)
    sx = (c > upper_f).fillna(False)
    return (le & ~lx).astype(bool), lx.astype(bool), (se & ~sx).astype(bool), sx.astype(bool)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["atr_mult"])).shift(1)
    return {"sl_stop": f}


def portfolio_kwargs(**params):
    return {}
