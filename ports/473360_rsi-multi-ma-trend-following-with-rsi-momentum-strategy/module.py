"""SMA 20 / 50 / 200 orderings with an RSI filter, daily bars: while the SMA 20 and 50 are both over the SMA 200 (in either order, or the 20 over the 200 over the 50) and the RSI is under 70 it goes long; the mirror orderings with the RSI over 30 go short; reversing. The 250-point target re-sent on every signal bar from that bar's close is not ported (pending).
Port of FMZ strategy #473360 "多均线趋势追踪与RSI动量策略-Multi-MA-Trend-Following-with-RSI-Momentum-Strategy" (Refined MA Strategy with Trailing Stop for 30m).

FMZ source id: 473360

Source
    https://www.fmz.com/strategy/473360 (PineScript v5, FMZ last modified 2024-11-29 15:20:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-130), SMA 20 / 50 / 200, RSI 14 (constants); target close +/- 250, trail_offset 25 (no trail_points)
    (s1 or s2 or s5) and rsi < 70 -> entry Long, exit(limit = close + 250, trail_offset = 25);  (s3 or s4 or s6) and rsi > 30 -> entry Short, exit(limit = close - 250, trail_offset = 25)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The scenarios used are s1 (20 > 50 > 200), s2 (50 > 20 > 200), s5 (20 > 200 > 50) for longs and
      s3 (200 > 50 > 20), s4 (50 > 200 > 20), s6 (200 > 20 > 50) for shorts; the equal-value scenarios
      feed no order. The conditions hold for many bars, so the exit is re-sent on nearly every bar from
      that bar's close: a level re-set every bar is not ported (as #438034, mark trailing_stop_pending);
      trail_offset without trail_points sets no trail (as #441084). Positions end at the opposite entry
      until then. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days;
      the title's "30m" is not the header).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA orderings with an RSI filter; per-bar target described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the point target stored.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473360_sma20_50_200_ordering_rsi_filter_reversal_target_pending"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    c = bars_df["close"]
    a, b, z = c.rolling(20).mean(), c.rolling(50).mean(), c.rolling(200).mean()
    r = _rsi(c, 14)
    up = ((a > b) & (b > z)) | ((b > a) & (a > z)) | ((a > z) & (z > b))
    dn = ((z > b) & (b > a)) | ((b > z) & (z > a)) | ((z > a) & (a > b))
    le = up & (r < 70)
    se = dn & (r > 30)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
