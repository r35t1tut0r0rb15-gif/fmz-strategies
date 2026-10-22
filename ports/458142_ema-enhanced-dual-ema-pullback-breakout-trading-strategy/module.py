"""EMA 8 pullback set-ups, daily bars, long only: after a 3-bar swing high, a low touching the EMA 8, then a high breaking over the swing high, the next low touching the EMA buys; there is no exit.
Port of FMZ strategy #458142 "改进型双重-EMA-回撤突破交易策略-Enhanced-Dual-EMA-Pullback-Breakout-Trading-Strategy" (8 EMA Pullback Strategy - Refined).

FMZ source id: 458142

Source
    https://www.fmz.com/strategy/458142 (PineScript v5, FMZ last modified 2024-07-30 12:04:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 189-235), EMA 8; swing high = high[2] < high[1] > high; flags waitingForPullback / waitingForBreakout / readyToTrigger
    swing high -> prevSwingHigh = high[1], wait for pullback;  waiting and low <= ema -> wait for breakout;  waiting and high > prevSwingHigh -> ready
    ready and low <= ema -> entry Long, ready = false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flag steps are followed in the written order, so one bar may pass several steps. The script
      has no exit at all: the first entry is held to the end of the data and later entries do nothing,
      as written (as #451391). Long only. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, swing-high pullback and breakout set-ups.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458142_ema8_swing_pullback_breakout_pullback_no_exit_long"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [8, 21],
}
DEFAULT_PARAMS = {"ema_len": 8}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    swing = ((h.shift(2) < h.shift(1)) & (h.shift(1) > h)).to_numpy()
    h1 = h.shift(1).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    le = np.zeros(m, dtype=bool)
    psh, w_pull, w_brk, ready = np.nan, False, False, False
    for i in range(m):
        if swing[i]:
            psh, w_pull, w_brk, ready = h1[i], True, False, False
        if w_pull and lv[i] <= e[i]:
            w_pull, w_brk = False, True
        if w_brk and hv[i] > psh:
            w_brk, ready = False, True
        if ready and lv[i] <= e[i]:
            le[i], ready = True, False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
