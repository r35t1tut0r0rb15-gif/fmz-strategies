"""One-minute bars: the signed volume (volume on an up close, minus volume on a down close) crossing over minus its 3-bar average goes long, crossing under plus its 3-bar average goes short; reversing (the script's exits send nothing).
Port of FMZ strategy #432879 "Quantitative Golden Cross Strategy" (@DankCoins - Customized Net Volume).

FMZ source id: 432879

Source
    https://www.fmz.com/strategy/432879 (PineScript v3, FMZ last modified 2023-11-22 14:39:33).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 137-173), source close; MAV 3; VHigh / VLow 50 / -50 (plots only); window 2018 ..
    nv = change(close) > 0 ? volume : change(close) < 0 ? -volume : 0;  MAV1 = sma(volume, 3), MAV2 = -MAV1
    crossover(nv, MAV2) -> entry Long Entry;  crossunder(nv, MAV1) -> entry Short Entry;  strategy.exit(..., when = exitLong / exitShort) with no price

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two strategy.exit calls carry only "when", with no profit, limit, loss, stop or trail: Pine
      sends no order for them, so a position ends only at the opposite entry (weird case). The signed
      volume is compared with its own 3-bar average, so only its shape matters. VHigh / VLow only feed
      plots. The author's window from 2018 is dropped. REVERSAL INTENDED. No sizing code. FREQ = "1min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, signed-volume crossings of its average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the signed volume and its 3-bar average; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 2018 .. 9999 window dropped).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432879_signed_volume_cross_avg_volume_1m_reversal"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mav_len": [3, 10, 20],
}
DEFAULT_PARAMS = {"mav_len": 3}


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
    ch = c.diff()
    nv = pd.Series(np.where(ch > 0, v, np.where(ch < 0, -v, 0.0)), index=c.index)
    mav1 = v.rolling(int(p["mav_len"])).mean()
    mav2 = -mav1
    long_c = (nv > mav2) & (nv.shift(1) <= mav2.shift(1))
    short_c = (nv < mav1) & (nv.shift(1) >= mav1.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return long_c, false, short_c, false.copy()


def portfolio_kwargs(**params):
    return {}
