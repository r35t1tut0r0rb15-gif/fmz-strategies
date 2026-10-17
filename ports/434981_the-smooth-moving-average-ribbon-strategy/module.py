"""Smoothed Heikin-Ashi ribbon, 1-hour bars: Heikin-Ashi candles smoothed three times by EMA 11 and turned into Heikin-Ashi
again give a ribbon; its close crossing above its open with the SMA 100 rising goes long, crossing below with the SMA
falling goes short; any other ribbon cross closes the position.
Port of FMZ strategy #434981 "The Smooth Moving Average Ribbon Strategy" (Smooth Moving Average Ribbon [STRATEGY] @PuppyTherapy).

FMZ source id: 434981

Source
    https://www.fmz.com/strategy/434981 (PineScript v4, FMZ last modified 2023-12-11 14:48:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 146-356), HA source on, MA EMA 11 x 3 smoothings, HA again on; filter SMA 100 rising / falling; start 2018
    [o, h, l, c] = smoothMA(HA(open, high, low, close), 3, "EMA", 11);  [o2, h2, l2, c2] = HA(o, h, l, c)
    crossover(c2, o2) and rising(sma100, 1) -> entry long;  crossunder(c2, o2) and falling(sma100, 1) -> entry short;  cross(c2, o2) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * smoothHA seeds its open with "o + c / 2" on the first bar (as written), then (open[1] +
      close[1]) / 2 of its own series. On a ribbon cross the new entry wins over the close_all (the
      position ends on the entry's side); a cross without the filter goes flat. The start date (2018)
      is the author's window: dropped. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed candle crosses and an average slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND431223 (2 members, best partner #431223, Jaccard 0.715); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434981_smooth_ha_ribbon"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [11, 21],
    "ma_length": [100, 50],
}
DEFAULT_PARAMS = {"length": 11, "loops": 3, "ma_length": 100}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _ha(o, h, lo, c):
    hac = (o + h + lo + c) / 4
    m = len(o)
    hao = np.zeros(m)
    for i in range(m):
        hao[i] = (o[i] + c[i] / 2) if i == 0 else (hao[i - 1] + hac[i - 1]) / 2
    hah = np.maximum(h, np.maximum(hao, hac))
    hal = np.minimum(lo, np.minimum(hao, hac))
    return hao, hah, hal, hac


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    n, loops = int(p["length"]), int(p["loops"])
    sm = []
    for x in _ha(o, h, lo, c):
        s = pd.Series(x)
        for _ in range(loops):
            s = s.ewm(span=n, adjust=False).mean()
        sm.append(s.to_numpy())
    o2, _, _, c2 = _ha(*sm)
    ma = bars_df["close"].rolling(int(p["ma_length"])).mean().to_numpy()
    ma1 = np.concatenate(([np.nan], ma[:-1]))
    a1 = np.concatenate(([np.nan], c2[:-1] - o2[:-1]))
    d = c2 - o2
    with np.errstate(invalid="ignore"):
        xu, xd = (d > 0) & (a1 <= 0), (d < 0) & (a1 >= 0)
        rising, falling = ma > ma1, ma < ma1
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if xu[i] or xd[i]:
            pos = 1 if (xu[i] and rising[i]) else (-1 if (xd[i] and falling[i]) else 0)
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
