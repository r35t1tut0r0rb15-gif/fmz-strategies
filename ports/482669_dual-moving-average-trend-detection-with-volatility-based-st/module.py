"""EMA 9 / 21 crossings, broker days: each crossing enters its side, with a stop 1.5 ATR 14 from the entry price; reversing.
Port of FMZ strategy #482669 "Dual Moving Average Trend Detection with Volatility Based Stop Loss Strategy" (EMA 9/21 + ATR SL Strategy).

FMZ source id: 482669

Source
    https://www.fmz.com/strategy/482669 (PineScript v5, FMZ last modified 2025-02-27 17:57:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 82-123), EMA 9 / 21; ATR 14 x 1.5 from the average price
    crossover(ema9, ema21) -> entry Long;  crossunder -> entry Short
    position > 0 -> exit Long (stop = avg - 1.5 atr);  position < 0 -> exit Short (stop = avg + 1.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is placed from the bar the position is held on and re-sent every bar with that bar's ATR
      around the fixed entry price: the port fixes it at the fill with the ATR of the signal bar (known at
      the fill open, section 7), a fraction of the fill price; the later ATR re-sets are kept pending (mark
      trailing_stop_pending). The crossings alternate and reverse. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop from the entry price as a fraction of the fill.
    2 generic: PASS, EMA crossings with an ATR stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_482669_ema9_21_cross_entry_atr15_stop_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 3.0],
    "ema_slow_len": [21, 50],
}
DEFAULT_PARAMS = {"atr_mult": 1.5, "ema_slow_len": 21, "ema_fast_len": 9, "atr_len": 14}


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


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["ema_fast_len"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow_len"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = _atr(bars_df, int(p["atr_len"])) * float(p["atr_mult"])
    sl_f = d.shift(1) / bars_df["open"]                  # the signal bar's ATR, from the fill price
    return {"sl_stop": sl_f.where(sl_f > 0)}


def portfolio_kwargs(**params):
    return {}
