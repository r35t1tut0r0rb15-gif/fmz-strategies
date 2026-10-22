"""EMA 12 / 26 crossings with the MACD 12 / 26 / 9 side, hourly bars: the up-cross with MACD over its signal goes long, the down-cross with MACD under it goes short, each with a 2 % stop and a 5 % target from the signal close; the opposite cross or the MACD side flipping closes; reversing.
Port of FMZ strategy #483121 "动态趋势动量交叉策略-基于双重EMA与MACD指标的量化交易系统-Dynamic-Trend-Momentum-Crossover-Strategy-Quantitative-Trading-System-Based-on-Dual-EMA-and-MACD-Indicators" (EMA + MACD Strategy).

FMZ source id: 483121

Source
    https://www.fmz.com/strategy/483121 (PineScript v5, FMZ last modified 2025-02-27 16:56:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-156), EMA 12 / 26; MACD 12 / 26 / 9; stop 2 %; target 5 %; 10 % of equity
    crossover(ema12, ema26) and macd > signal -> entry Long + exit(stop = close x 0.98, limit = close x 1.05);  crossunder and macd < signal -> entry Short + mirror
    crossunder(ema12, ema26) or macd < signal -> close Long;  crossover or macd > signal -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EMA 12 / 26 pair is the MACD line itself, so its crossings are the MACD's zero crossings, as
      written. The levels are fixed at the signal close and sent as fractions of the fill open (a level
      at or through it is marketable and closed one bar late, as #458256); the crossings alternate. A
      close on the bar of an entry is masked by the entry; an entry on the other side reverses (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (driver D4). The 10 % of equity size is sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with the MACD side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_483121_ema12_26_cross_macd_side_2_5pct_bracket_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss_perc": [2.0, 1.0],
    "take_profit_perc": [5.0, 3.0],
}
DEFAULT_PARAMS = {"stop_loss_perc": 2.0, "take_profit_perc": 5.0, "short_ema": 12, "long_ema": 26,
                  "macd_fast": 12, "macd_slow": 26, "macd_signal": 9}


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


def _signals(bars_df, p):
    c = bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    es, el = ema(c, p["short_ema"]), ema(c, p["long_ema"])
    macd = ema(c, p["macd_fast"]) - ema(c, p["macd_slow"])
    sig = ema(macd, p["macd_signal"])
    xu = (es > el) & (es.shift(1) <= el.shift(1))
    xd = (es < el) & (es.shift(1) >= el.shift(1))
    le, se = xu & (macd > sig), xd & (macd < sig)
    lx, sx = xd | (macd < sig), xu | (macd > sig)
    a, b = float(p["stop_loss_perc"]) / 100, float(p["take_profit_perc"]) / 100
    lvl = {"l_sl": c * (1 - a), "l_tp": c * (1 + b), "s_sl": c * (1 + a), "s_tp": c * (1 - b)}
    return le, se, lx, sx, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lx, sx, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, (lx | (lf & l_thr)) & ~le & ~se, se, (sx | (sf & s_thr)) & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
