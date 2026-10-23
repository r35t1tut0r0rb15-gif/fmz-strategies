"""Hourly bars, effectively long only: the close of 3 bars ago crossing over the lower Bollinger band (14, 2 x 1 sd) on volume above its SMA 14 goes long; the close of 3 bars ago crossing under the upper band on such volume closes it (the short it opens is stopped at once).
Port of FMZ strategy #437754 "Breakout and Intelligent Bollinger Bands Price Channel Strategy" (DZ Strategy ICT).

FMZ source id: 437754

Source
    https://www.fmz.com/strategy/437754 (PineScript v5, FMZ last modified 2024-01-05 13:14:11).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 158-337), five identical sets (1 / 5 / 15 / 60 / 240 labels, all length 14, deviations 2, multiplier 1, displacement 3, volume threshold 1); stop 1 / 3 under the average price
    buySignal = crossover(close[3], sma(close, 14) - 2 stdev(close, 14)) and volume > sma(volume, 14) -> entry Achat (x5);  sellSignal = crossunder(close[3], upper) and volume > sma -> entry Vente (x5)
    exit("Stop Loss 1 min", "Achat 1 min", stop = avg x 2 / 3);  exit("Stop Loss 1 min", "Vente 1 min", stop = avg x 2 / 3)  (same id per set)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The five "timeframe" sets have identical inputs on the chart's own bars, so they fire together; with
      the default pyramiding only the first entry of a side opens. Each set's two exits share one id, so
      the second (from_entry the short) replaces the first: longs get no stop, and a short gets a stop at
      avg x 2 / 3, BELOW its entry, which fills as soon as the short opens (weird case). A sell signal
      therefore only closes the long: ported as the long's exit. The volume test compares the bar with its
      own SMA. The fib levels feed nothing. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, displaced Bollinger re-entries with a volume filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > sma(volume, 14); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437754_displaced_bb14_reentry_volume_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "displacement": [3, 1],
}
DEFAULT_PARAMS = {"length": 14, "deviations": 2.0, "multiplier": 1.0, "displacement": 3, "vol_threshold": 1.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    rng = float(p["multiplier"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + float(p["deviations"]) * rng, basis - float(p["deviations"]) * rng
    cd = c.shift(int(p["displacement"]))
    vok = v > float(p["vol_threshold"]) * v.rolling(n).mean()
    buy = ((cd > lower) & (cd.shift(1) <= lower.shift(1)) & vok).to_numpy()
    sell = ((cd < upper) & (cd.shift(1) >= upper.shift(1)) & vok).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and buy[i] and not sell[i]:
            le[i], pos = True, 1
        elif pos == 1 and sell[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
