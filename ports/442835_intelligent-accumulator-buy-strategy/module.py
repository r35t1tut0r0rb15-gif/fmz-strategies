"""RSI 7 against a one-deviation band of its own SMA 14, daily bars, long only: the RSI under its lower band goes long; over its upper band closes (the "accumulator" adds are refused at the default
pyramiding).
Port of FMZ strategy #442835 "Intelligent Accumulator Buy Strategy" (TTP Intelligent Accumulator).

FMZ source id: 442835

Source
    https://www.fmz.com/strategy/442835 (PineScript v5, FMZ last modified 2024-02-26 13:59:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 212-262), RSI 7; SMA 14 and stdev 14 of the RSI; add while in profit off; exit 100 % per candle; external sources off
    intEntry = rsi < sma(rsi, 14) - stdev(rsi, 14);  intExit = rsi > sma + stdev;  entry and (opentrades == 0 or not addWhileInProfit or close < avg) -> entry long
    exit and opentrades > 0 -> close long (qty_percent 100)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() call sets no pyramiding, so the default refuses every further "long" while one is
      open: one long at a time, not an accumulation (as #442635). The exit closes 100 % of the position.
      The external-source inputs are off. Pine's stdev is the population deviation. Long only. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI against its own deviation band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442835_rsi7_own_band_dip_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [7, 14],
    "band_len": [14, 30],
}
DEFAULT_PARAMS = {"rsi_len": 7, "band_len": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["band_len"])
    mid, sd = r.rolling(n).mean(), r.rolling(n).std(ddof=0)
    le = r < mid - sd
    lx = r > mid + sd
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
