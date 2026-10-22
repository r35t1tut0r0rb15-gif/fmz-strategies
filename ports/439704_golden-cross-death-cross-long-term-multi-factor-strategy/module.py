"""SMA 10 / 50 golden crosses under RSI 70 with an ATR bracket, long only, broker days: the SMA 10 crossing over the SMA 50 with the RSI 14 under 70 goes long with a stop 1.5 ATR(14) under the signal close and
a target 3 ATR over it.
Port of FMZ strategy #439704 "Golden Cross Death Cross Long term Multi factor Strategy" (Long Only Multi-Indicator Strategy).

FMZ source id: 439704

Source
    https://www.fmz.com/strategy/439704 (PineScript v4, FMZ last modified 2024-01-23 11:11:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-172), SMA 10 / 50; RSI 14, overbought 70 (oversold unused); ATR 14; risk multiplier 1.5
    longCondition = crossover(sma10, sma50) and rsi < 70 -> entry Long, exit(SL Long, stop = close - 1.5 atr), exit(TP Long, limit = close + 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two exits are sent on the signal bar at levels from its close and stay in force: sl_stop = 1.5
      x ATR(14) / close and tp_stop = 3 x ATR(14) / close of the signal bar, shifted one bar inside
      stops() and re-based on the fill. A new signal while long would move the levels; the port keeps the
      first. Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark
      coarse_bar_stop. No sizing code. Daily bars are broker days, stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, SMA crossings, RSI and ATR distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk multiplier stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_439704_sma10_50_golden_rsi_atr_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "risk_mult": [1.5, 3.0],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"risk_mult": 1.5, "slow": 50, "fast": 10, "rsi_len": 14, "overbought": 70, "atr_len": 14}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _signal(bars_df, p):
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    return (f > s) & (f.shift(1) <= s.shift(1)) & (_rsi(c, int(p["rsi_len"])) < float(p["overbought"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    false = pd.Series(False, index=bars_df.index)
    return _signal(bars_df, p), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["risk_mult"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": a.shift(1), "tp_stop": (2 * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
