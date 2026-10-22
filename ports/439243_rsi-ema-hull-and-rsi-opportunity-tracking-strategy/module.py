"""Hull / EMA 50 crossings with an RSI filter, broker days: a Hull 7 crossing over the EMA 50 with the RSI 14 over 60 goes long; the EMA 50 crossing over the Hull with the RSI under 45 goes short; reversing.
Port of FMZ strategy #439243 "基于均线和RSI的机会跟踪策略EMA-Hull-and-RSI-Opportunity-Tracking-Strategy" (Simple EMA_Hull_RSI).

FMZ source id: 439243

Source
    https://www.fmz.com/strategy/439243 (PineScript v4, FMZ last modified 2024-01-18 15:46:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-156), EMA 50 of close; RSI 14 overbought 60, oversold 45; Hull length 7
    n1 = wma(2 wma(close, round(n / 2)) - wma(close, n), round(sqrt(n)));  long = rsi > 60 and crossover(n1, ema 50);  short = rsi < 45 and crossover(ema 50, n1)
    entry EHR_Long when long;  entry EHR_Short when short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Hull follows the script's rounding: Pine round (half away from zero), so Hull 7 uses WMA 4 and
      7, smoothed by WMA 3. The [1] Hull (n2) only colours the plot. strategy.entry reverses: REVERSAL
      INTENDED. The fixed cash size is sizing; the commission is a cost. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Hull / EMA crossings and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash size and the commission stored.
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

NAME = "fmz_439243_hull_ema50_cross_rsi_filter"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [50, 100],
    "hull_len": [7, 14],
}
DEFAULT_PARAMS = {"ema_len": 50, "hull_len": 7, "overbought": 60, "oversold": 45, "rsi_len": 14}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _pround(x):
    return int(np.floor(x + 0.5))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["hull_len"])
    n1 = _wma(2 * _wma(c, _pround(n / 2)) - _wma(c, n), _pround(np.sqrt(n)))
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    up = (r > float(p["overbought"])) & (n1 > e) & (n1.shift(1) <= e.shift(1))
    dn = (r < float(p["oversold"])) & (e > n1) & (e.shift(1) <= n1.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
