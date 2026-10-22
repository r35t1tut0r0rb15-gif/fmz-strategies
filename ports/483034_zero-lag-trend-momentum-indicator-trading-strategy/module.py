"""A zero-lag EMA 50 trend score (how many of the last 50 values it beats) with an ATR band, broker days: a score over 5 with the close over the line plus 1.5 x the 150-bar highest ATR 50 goes long, the mirror goes short; reversing.
Port of FMZ strategy #483034 "Zero Lag Trend Momentum Indicator Trading Strategy" (Zero Lag Trend Strategy).

FMZ source id: 483034

Source
    https://www.fmz.com/strategy/483034 (PineScript v6, FMZ last modified 2025-02-21 10:19:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-157), length 50; zero-lag EMA (menu default); volatility 1.5 x highest(ATR 50, 150); score loop 1-50, thresholds 5 / -5; target 8 %; stop 0 %; MPL 2.0 notice (josephdelvecchio)
    zl = ema(2 close - close[24], 50);  score = sum over i = 1..50 of sign(zl - zl[i]);  vol = highest(atr(50), 150) x 1.5
    score > 5 and close > zl + vol -> entry Long;  else score < -5 and close < zl - vol -> entry Short
    every bar: exit Long (stop = close x 1.00, limit = close x 1.08);  exit Short (stop = close x 1.08, limit = close x 1.00)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-sent on every bar from that bar's close (the long's stop AT the close, the short's
      limit at the close), so their levels follow the price: not ported, mark trailing_stop_pending (as
      the C170-C175 readings); the opposite entry is the exit. The entries are states; a repeat on the
      side held adds nothing, the other side reverses (REVERSAL INTENDED). The "Timeframe" input feeds
      nothing; the moving-average menu keeps its default (ema). No sizing code. The MPL 2.0 notice is kept
      with the verbatim copy (ported, stated). Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent close exits pending.
    2 generic: PASS, zero-lag trend score with an ATR band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483034_zero_lag_ema50_score_atr_band_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 30],
    "volatility_mult": [1.5, 1.0],
}
DEFAULT_PARAMS = {"length": 50, "volatility_mult": 1.5, "loop_start": 1, "loop_end": 50, "threshold_up": 5,
                  "threshold_down": -5}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, n)
    lag = (n - 1) // 2
    zl = (2 * c - c.shift(lag)).ewm(span=n, adjust=False).mean()
    vol = atr.rolling(n * 3).max() * float(p["volatility_mult"])
    score = pd.Series(0.0, index=c.index)
    for i in range(int(p["loop_start"]), int(p["loop_end"]) + 1):
        prev = zl.shift(i)
        score = score + (zl > prev).astype(float) - (zl < prev).astype(float)
    le = (score > float(p["threshold_up"])) & (c > zl + vol)
    se = (score < float(p["threshold_down"])) & (c < zl - vol) & ~le
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
