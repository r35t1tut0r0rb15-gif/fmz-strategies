"""EMA 56 slope angle with a rate-of-change gate, broker days: while the ROC 12 average is outside +/- 1 %, a non-negative EMA slope (in ATR units) holds a long and a non-positive one a short; each trade has a
2 % stop; reversing.
Port of FMZ strategy #439979 "Trend Angle Moving Average Crossover Strategy" (Trend Angle BF).

FMZ source id: 439979

Source
    https://www.fmz.com/strategy/439979 (PineScript v4, FMZ last modified 2024-01-25 14:35:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-267), source ohlc4; EMA 56; JMA 10 / 50 / 1 (plot only); ROC 12, change 2; stop 2 %, target 900 %; test period true
    ma_slope = degrees(atan((ema - ema[1]) / atr(14)));  isMoving = ema(roc(12), 6) > 1 or < -1;  long = ma_slope >= 0 and isMoving;  short = ma_slope <= 0 and isMoving
    entry Long when long, entry Short when short;  exit(stop = avg x 0.98 / 1.02, limit = avg x 10 / -8) from the bar after the regime's signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * The slope is the angle of the EMA change over the ATR, so it is scale-free. A flat slope meets both
      tests and the later short wins (as #437773). The stop is a fixed 2 % of the average (fill) price,
      sent while in the regime from the bar after its signal: the port starts it at the fill (sl_stop
      0.02); the 900 % target cannot be reached in practice and is dropped. A long stopped out re-enters
      on the next bar of the state. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. No sizing code. Daily
      bars are broker days, stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent stop from the fill.
    2 generic: PASS, EMA slope angle and ROC gate.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_439979_ema56_slope_angle_roc_gate"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_len": [56, 30],
    "pcnt_change": [2, 4],
}
DEFAULT_PARAMS = {"ma_len": 56, "pcnt_change": 2, "roc_len": 12, "sl": 0.02}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    e = src.ewm(span=int(p["ma_len"]), adjust=False).mean()
    with np.errstate(divide="ignore", invalid="ignore"):
        slope = np.degrees(np.arctan((e - e.shift(1)) / _atr(bars_df, 14)))
    n = int(p["roc_len"])
    roc = 100 * (c - c.shift(n)) / c.shift(n)
    er = roc.ewm(span=n // 2, adjust=False).mean()
    half = float(p["pcnt_change"]) / 2
    moving = (er > half) | (er < -half)
    long_ = (slope >= 0) & moving
    short_ = (slope <= 0) & moving
    false = pd.Series(False, index=c.index)
    return long_ & ~short_, false, short_, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}
