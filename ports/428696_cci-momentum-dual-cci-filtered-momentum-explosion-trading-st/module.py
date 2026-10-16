"""EMA 8 / SMA 26 cross confirmed by two CCIs, the SMA's 5-bar momentum and RSI 26, broker days: an up
cross with everything positive goes long, a down cross with everything negative goes short.
Port of FMZ strategy #428696 "双CCI滤波momentum爆发交易策略Dual-CCI-Filtered-Momentum-Explosion-Trading-Strategy" (Momentum Explosion 2CCI RSI).

FMZ source id: 428696

Source
    https://www.fmz.com/strategy/428696 (PineScript v4, FMZ last modified 2023-10-08 14:10:41).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 145-161), EMA 8, SMA 26, CCI 34 / 55, RSI 26 vs 48
    crossover(ema8, sma26) and mom(sma26,5) > 0 and cci34 > 0 and cci55 > 0 and rsi26 > 48 -> entry long
    crossunder(ema8, sma26) and mom(sma26,5) < 0 and cci34 < 0 and cci55 < 0 and rsi26 < 48 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * cci(close, n) = (close - SMA n) / (0.015 x mean absolute deviation from that SMA), n bars
      including the current one; mom(x, 5) = x - x[5].
    * strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, sign tests and an RSI level only.
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

NAME = "fmz_428696_ema_sma_cross_two_cci"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cci_fast": [34, 20],
    "rsi_level": [48, 50],
}
DEFAULT_PARAMS = {"ema_length": 8, "sma_length": 26, "mom_length": 5, "cci_fast": 34, "cci_slow": 55,
                  "rsi_length": 26, "rsi_level": 48}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _cci(x, n):
    ma = x.rolling(n).mean()
    md = x.rolling(n).apply(lambda w: np.mean(np.abs(w - w.mean())), raw=True)
    return (x - ma) / (0.015 * md.replace(0.0, np.nan))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    sma = c.rolling(int(p["sma_length"])).mean()
    mom = sma - sma.shift(int(p["mom_length"]))
    c1, c2 = _cci(c, int(p["cci_fast"])), _cci(c, int(p["cci_slow"]))
    r = _rsi(c, int(p["rsi_length"]))
    up = (ema > sma) & (ema.shift(1) <= sma.shift(1))
    dn = (ema < sma) & (ema.shift(1) >= sma.shift(1))
    long_e = (up & (mom > 0) & (c1 > 0) & (c2 > 0) & (r > p["rsi_level"])).astype(bool)
    short_e = (dn & (mom < 0) & (c1 < 0) & (c2 < 0) & (r < p["rsi_level"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
