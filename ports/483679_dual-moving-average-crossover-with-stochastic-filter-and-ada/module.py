"""Close crossings of the SMA 34 with the SMA 34 / 200 trend and a Stochastic 9 / 3 / 3 filter, hourly bars: crossing up in an uptrend with %K over 20 goes long, crossing down in a downtrend with %K under 80 goes short, each with a 2 % stop and a 4 % target from the fill; reversing.
Port of FMZ strategy #483679 "Dual Moving Average Crossover with Stochastic Filter and Adaptive Trailing Stop Strategy" ([DRAGON]SMA 34 & SMA 200 with Stochastic 9-3-3 & Trailing Stop (Price Chart)).

FMZ source id: 483679

Source
    https://www.fmz.com/strategy/483679 (PineScript v6, FMZ last modified 2025-02-25 11:05:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 168-226), SMA 34 / 200; Stochastic 9 / 3 / 3; stop 2 %; target 4 %; break-even after 2 %; 10 % of equity
    crossover(close, sma34) and sma34 > sma200 and k > 20 -> entry Long + exit(stop = close >= avg x 1.02 ? avg : avg x 0.98, limit = avg x 1.04)
    crossunder(close, sma34) and sma34 < sma200 and k < 80 -> entry Short + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is sent only on signal bars, around the average price, which is na on a flat signal bar
      (the other side's price on a reversal); it is ported as the 2 % / 4 % bracket around the fill,
      active from the fill bar (as #440797). A repeat signal while held re-sends it, possibly with the
      break-even stop: mark trailing_stop_pending. An entry on the other side reverses (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (driver D4). The 10 % of equity size is sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, SMA crossings with a trend and Stochastic filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_483679_close_sma34_cross_sma200_trend_stoch_2_4pct_bracket_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss_percent": [2.0, 1.0],
    "take_profit_percent": [4.0, 2.0],
}
DEFAULT_PARAMS = {"stop_loss_percent": 2.0, "take_profit_percent": 4.0, "sma_fast": 34, "sma_slow": 200,
                  "sto_k": 9, "sto_smooth": 3}


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
    f, s = c.rolling(int(p["sma_fast"])).mean(), c.rolling(int(p["sma_slow"])).mean()
    n = int(p["sto_k"])
    rng = h.rolling(n).max() - lo.rolling(n).min()
    k = (100 * (c - lo.rolling(n).min()) / rng.where(rng > 0)).rolling(int(p["sto_smooth"])).mean()
    le = (c > f) & (c.shift(1) <= f.shift(1)) & (f > s) & (k > 20)
    se = (c < f) & (c.shift(1) >= f.shift(1)) & (f < s) & (k < 80)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    sl = pd.Series(float(p["stop_loss_percent"]) / 100, index=idx).shift(1)
    tp = pd.Series(float(p["take_profit_percent"]) / 100, index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
