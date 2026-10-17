"""Closes outside the Bollinger bands with a 2 ATR stop and a 4 ATR target, broker days: every close under the lower band
is a long entry and every close over the upper band a short entry; each trade has a stop 2 ATR and a target 4 ATR
from the signal close.
Port of FMZ strategy #484580 "布林带ATR风险回报比交易策略-Bollinger-Bands-ATR-Risk-Reward-Trading-Strategy" (Bollinger Bands & ATR Strategy).

FMZ source id: 484580

Source
    https://www.fmz.com/strategy/484580 (PineScript v5, FMZ last modified 2025-03-03 09:56:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 188-217), BB 20 x 2, ATR 14, stop 2 ATR, RR 2
    close < lower -> entry long + exit(limit = close + 4 ATR, stop = close - 2 ATR)  (short mirrored over the upper band)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every condition bar is an entry; the bracket is fixed at the signal bar: sl_stop = 2 x ATR / close, tp_stop = rr x
      that, shifted one bar inside stops() and re-based on the fill (house rule). Consecutive signal bars while held
      re-place it: mark trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header:
      coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, bands and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484580_outside_bollinger_atr_bracket"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_dev": [2.0, 2.5],
    "rr": [2.0, 1.5],
}
DEFAULT_PARAMS = {"bb_length": 20, "bb_dev": 2.0, "atr_len": 14, "sl_atr": 2.0, "rr": 2.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = p["bb_dev"] * c.rolling(n).std(ddof=0)
    false = pd.Series(False, index=bars_df.index)
    return (c < basis - dev).astype(bool), false, (c > basis + dev).astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
