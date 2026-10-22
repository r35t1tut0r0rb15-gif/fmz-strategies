"""Closes under the lower Bollinger band (20, 1) with the RSI 14 above 42 buy, daily bars, long only. The 6.604 % / 2.328 % bracket from the average price is armed only by the exit condition inside a trade
and is not ported, so the port has no exit (one long held from the first signal).
Port of FMZ strategy #445786 "Flawless-Victory-DCA-动量与波动率策略Flawless-Victory-DCA-Momentum-and-Volatility-Strategy" (Flawless Victory DCA Strategy).

FMZ source id: 445786

Source
    https://www.fmz.com/strategy/445786 (PineScript v4, FMZ last modified 2024-03-22 10:54:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 130-187), RSI 14 (42 / 70); BB 20 / 1; stop 6.604 %, take profit 2.328 % of the average price; DCA off; 100 % of equity, capital 100000
    close < lower and rsi > 42 -> entry Long (DCA off);  exit(stop = avg x (1 - 6.604 %), limit = avg x (1 + 2.328 %), when = close > upper and rsi > 70)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit is created only on a bar where the close is above the upper band with the RSI over
      70, with levels from the position's average price: the bracket appears only on such a bar inside
      the trade and then stays. A stop that starts after entry cannot be expressed by stops(): the
      bracket is not ported (as #437800) and the module gets the mark trailing_stop_pending (the
      intended bracket is owed). Without it the port has no exit. DCA is off by default, so every buy
      is the single "Long" id (pyramiding 0: one position). Long only. The 100 % of equity size is
      sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the late-armed bracket not ported (mark).
    2 generic: PASS, lower-band closes with an RSI guard.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size stored; the percent bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_445786_lower_band_rsi_guard_long_entries"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "rsi_lower": [42, 30],
}
DEFAULT_PARAMS = {"length": 20, "rsi_lower": 42.0, "mult": 1.0}


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
    c = bars_df["close"]
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), 14), _rma((-d).clip(lower=0), 14)
    with np.errstate(divide="ignore", invalid="ignore"):
        base = 100 - 100 / (1 + up / dn)
    # down == 0 ? 100 : up == 0 ? 0 : formula (na stays na)
    rsi = pd.Series(np.where(dn == 0, 100.0, np.where(up == 0, 0.0, base)), index=c.index)
    n = int(p["length"])
    lower = c.rolling(n).mean() - float(p["mult"]) * c.rolling(n).std(ddof=0)
    le = (c < lower) & (rsi > float(p["rsi_lower"]))
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
