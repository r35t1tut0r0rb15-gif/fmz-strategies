"""RSI 14 extremes with a 0.2 % stop / 0.6 % target, daily (broker-day) bars: RSI(14) at or below 30 goes long; at
or above 70 goes short.
Port of FMZ strategy #483518 "基于RSI动量指标的自适应交易策略-Adaptive-Trading-Strategy-Based-on-RSI-Momentum-Indicator" (MultiSymbol Smart Money EA without Lot Sizes or Pairs).

FMZ source id: 483518

Source
    https://www.fmz.com/strategy/483518 (PineScript v5, FMZ last modified 2025-02-27 16:47:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 96-131), RSI 14, 30 / 70, SL 0.2 %, TP 0.6 %
    long = rsi <= 30 -> entry long; short = rsi >= 70 -> entry short
    while long: exit(stop = close x 0.998, limit = close x 1.006) on every bar (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-issued on every bar while held from the CURRENT close (longPrice = close): a moving level.
      Fixed at the entry as 0.2 % / 0.6 % fractions of the fill (house rule), mark trailing_stop_pending (desktop
      convention).
    * Every bar in the zone is an entry signal (a same-side entry while held is ignored). Entries reverse
      (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4).
    * Daily bars are broker days (17:00 America/New_York), each stamped with its first minute (as #430984). Stops on
      daily bars: mark coarse_bar_stop. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (marked).
    2 generic: PASS, RSI and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483518_rsi_extremes_tight_pct_bracket"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.2, 1.0],
    "tp_pct": [0.6, 3.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_ob": 70.0, "rsi_os": 30.0, "sl_pct": 0.2, "tp_pct": 0.6}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rsi = _rsi(bars_df["close"], int(p["rsi_len"]))
    long_e = (rsi <= p["rsi_os"]).astype(bool)
    short_e = (rsi >= p["rsi_ob"]).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
