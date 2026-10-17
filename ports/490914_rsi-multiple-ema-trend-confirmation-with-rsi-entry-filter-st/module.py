"""Four-EMA stack with an RSI 60 cap, long only, broker days: with EMA 9 > 21 > 63 > 200, a close above EMA 9 and
RSI 14 at or below 60 the strategy goes long; EMA 21 crossing below EMA 63 closes the long.
Port of FMZ strategy #490914 "多重指数移动平均线趋势确认与RSI过滤入场策略-Multiple-EMA-Trend-Confirmation-with-RSI-Entry-Filter-Strategy" (4 EMAs with Entry and Exit Strategy).

FMZ source id: 490914

Source
    https://www.fmz.com/strategy/490914 (PineScript v5, FMZ last modified 2025-04-17 14:33:40).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 176-213), EMA 9 / 21 / 63 / 200, RSI 14 <= 60
    long = ema9 > ema21 > ema63 > ema200 and close > ema9 and rsi <= 60 -> entry long
    crossunder(ema21, ema63) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The commented-out EMA 126 and RSI 80 / 40 %-above exits are not code; not used. The commission in strategy() is
      a cost: not in the module (costs come from the cost model).
    * An entry and the exit cannot fall on one bar (the stack needs EMA 21 above EMA 63).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. Long only.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs and an oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_490914_four_ema_stack_rsi_cap_long"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_cap": [60, 70],
    "ema_mid": [63, 50],
}
DEFAULT_PARAMS = {"ema_fast": 9, "ema_short": 21, "ema_mid": 63, "ema_long": 200, "rsi_len": 14, "rsi_cap": 60}


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
    c = bars_df["close"]
    e = {k: c.ewm(span=int(p[k]), adjust=False).mean() for k in ("ema_fast", "ema_short", "ema_mid", "ema_long")}
    rsi = _rsi(c, int(p["rsi_len"]))
    bull = (e["ema_fast"] > e["ema_short"]) & (e["ema_short"] > e["ema_mid"]) & (e["ema_mid"] > e["ema_long"])
    entry = (bull & (c > e["ema_fast"]) & (rsi <= p["rsi_cap"])).astype(bool)
    exit_ = ((e["ema_short"] < e["ema_mid"]) & (e["ema_short"].shift(1) >= e["ema_mid"].shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return entry, exit_, false, false.copy()


def portfolio_kwargs(**params):
    return {}
