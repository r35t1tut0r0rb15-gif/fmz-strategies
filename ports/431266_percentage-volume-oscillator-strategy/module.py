"""HPotter's Percentage Volume Oscillator (EMA 12 against EMA 26 of volume) against its EMA 9 signal, hourly bars: the PVO under its signal goes long, above it goes short (held on a tie); reversing.
Port of FMZ strategy #431266 "Percentage Volume Oscillator Strategy" (Percentage Volume Oscillator (PVO)).

FMZ source id: 431266

Source
    https://www.fmz.com/strategy/431266 (PineScript v2, FMZ last modified 2023-11-06 15:45:02).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 162-180), EMA 12 / 26 of volume, signal EMA 9; reverse off
    xPVO = (ema(volume, 12) - ema(volume, 26)) / ema(volume, 26) x 100;  pos = signal < xPVO ? -1 : signal > xPVO ? 1 : pos[1];  1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A rising volume oscillator (PVO over its signal) is read as SHORT and a falling one as long, as
      written. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume oscillator against its signal.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the PVO of volume EMAs 12 / 26; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431266_percentage_volume_oscillator_signal_state_reversal"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_ema": [12, 5],
    "long_ema": [26, 34],
}
DEFAULT_PARAMS = {"short_ema": 12, "long_ema": 26, "signal_ema": 9}


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
    v = bars_df["volume"]
    es = v.ewm(span=int(p["short_ema"]), adjust=False).mean()
    el = v.ewm(span=int(p["long_ema"]), adjust=False).mean()
    pvo = (es - el) / el.where(el != 0) * 100
    sig = pvo.ewm(span=int(p["signal_ema"]), adjust=False).mean()
    raw = np.where(sig < pvo, -1, np.where(sig > pvo, 1, 0))
    pos = np.zeros(len(raw), dtype=np.int8)
    q = 0
    for i in range(len(raw)):
        if raw[i] != 0:
            q = raw[i]
        pos[i] = q
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((pos == 1) & (prev != 1), index=ix), false,
            pd.Series((pos == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
