"""2-hour bars, long only: the SMA 9 crossing over the SMA 21 on volume above 1.5 x its 20-bar average and above the previous bar's goes long; the SMA crossing back under closes it, and so does a low under 2 % below the FIRST trade's entry price (the script never resets it).
Port of FMZ strategy #482421 "Trend Breakout Trading Strategy Based on Dual Moving Averages and Volume" (MA Crossover with Volume (Long Only) + Stop Loss).

FMZ source id: 482421

Source
    https://www.fmz.com/strategy/482421 (PineScript v5, FMZ last modified 2025-02-18 13:38:51).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 120-173), SMA 9 / 21; volume SMA 20 x 1.5 and > volume[1]; stop 2 % of the stored entry price
    longCondition = crossover(shortMa, longMa) and volume > volumeMa x 1.5 and volume > volume[1] -> entry Long;  crossunder(shortMa, longMa) -> close Long
    var entryPrice = na;  if position_size > 0 and na(entryPrice): entryPrice := position_avg_price;  position_size > 0 and low < entryPrice x 0.98 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * entryPrice is set once, on the first bar of the first trade, and never set back to na, so every
      later trade uses the first trade's fill for its 2 % stop test (weird case): a later trade entered
      far above it never stops, one entered below it closes at once. The stop is a low test at the bar's
      close, so the close fills at the next open (in the signals). The closes act on the position held
      at the bar's close. Long only. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; low-checked stop from the first entry price, in the signals.
    2 generic: PASS, SMA crossings on rising high volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 20 and the previous bar's; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482421_sma9_21_cross_rising_volume_first_entry_stop_2h_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sl": [0.02, 0.05],
    "fast": [9, 12],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "vol_mult": 1.5, "sl": 0.02}


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
    o, lo, c, v = bars_df["open"], bars_df["low"], bars_df["close"], bars_df["volume"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    vol_ok = (v > v.rolling(20).mean() * float(p["vol_mult"])) & (v > v.shift(1))
    buy = ((f > s) & (f.shift(1) <= s.shift(1)) & vol_ok).to_numpy()
    xu = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    on, ln = o.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    k = 1 - float(p["sl"])
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, held_prev, ep, fill = 0, 0, np.nan, np.nan
    for i in range(m):
        held = pos                          # the position after this bar's open
        if held == 1 and held_prev == 0:
            fill = on[i]
        if held == 1 and np.isnan(ep):
            ep = fill                       # set once, never reset
        new = held
        if buy[i] and held == 0:
            new = 1
        if held == 1 and (ln[i] < ep * k or xu[i]):
            new = 0
        if new != held and i + 1 < m:
            if new == 1:
                le[i] = True
            else:
                lx[i] = True
            pos = new
        held_prev = held
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
