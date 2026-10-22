"""A "snake line" averaging a hand-built ADX 14, Stochastic RSI 14 x 100 and CCI 14 against its own 100-bar 20 % / 80 % levels, broker days: crossing up through the 20 % level goes long, crossing down through the 80 % level goes short; reversing.
Port of FMZ strategy #483038 "Dynamic Multi Indicator Trend Recognition Strategy with Triple Sync Analysis" (Triple Sync Strategy).

FMZ source id: 483038

Source
    https://www.fmz.com/strategy/483038 (PineScript v6, FMZ last modified 2025-02-21 10:31:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-134), base period 14; dynamic lookback 100; levels at 20 % / 80 % of the 100-bar range
    dmi+ = rma(max(change(high), 0), 14);  dmi- = rma(max(-change(low), 0), 14);  adx = rma(|dmi+ - dmi-| / (dmi+ + dmi-) x 100, 14)
    stochRsi = (rsi - lowest(rsi, 14)) / (highest(rsi, 14) - lowest(rsi, 14));  cci = cci(close, 14);  snake = (adx + 100 stochRsi + cci) / 3
    crossover(snake, low + 0.2 range) -> close Short, entry Long;  crossunder(snake, low + 0.8 range) -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ADX is kept as written (raw moves smoothed, with no true-range scaling and no comparison of the
      two moves). The levels come from the snake line's own 100-bar extremes including the bar. Each
      crossing closes the other side and enters: REVERSAL INTENDED. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, composite oscillator against its own range levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483038_adx_stochrsi_cci_snake_range_20_80_cross_reversal"
FAMILY = "multi_indicator_vote"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 10],
    "dyn_len": [100, 50],
}
DEFAULT_PARAMS = {"length": 14, "dyn_len": 100}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _cci(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.lib.stride_tricks.sliding_window_view(v, n)
        mu = w.mean(axis=1)
        md = np.abs(w - mu[:, None]).mean(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            out[n - 1:] = (v[n - 1:] - mu) / (0.015 * md)
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    dp = _rma(h.diff().clip(lower=0), n)
    dm = _rma((-lo.diff()).clip(lower=0), n)
    adx = _rma((dp - dm).abs() / (dp + dm) * 100, n)
    r = _rsi(c, n)
    rr = r.rolling(n).max() - r.rolling(n).min()
    srsi = (r - r.rolling(n).min()) / rr.where(rr != 0)
    snake = (adx + srsi * 100 + _cci(c, n)) / 3
    k = int(p["dyn_len"])
    sh, sl = snake.rolling(k).max(), snake.rolling(k).min()
    dr = sh - sl
    up_l, lo_l = sl + dr * 0.8, sl + dr * 0.2
    le = (snake > lo_l) & (snake.shift(1) <= lo_l.shift(1))
    se = (snake < up_l) & (snake.shift(1) >= up_l.shift(1))
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
