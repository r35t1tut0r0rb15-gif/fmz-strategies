"""Broker days: any two of (RSI 14 crossing over 30, the MACD 12 / 26 / 9 histogram crossing over 0, relative volume crossing over 2) on one bar goes long; any two of (RSI crossing under 70, the histogram crossing under 0, relative volume crossing under 5) goes short; reversing.
Port of FMZ strategy #439081 "融合MACDRSI和RVOL的量化交易策略Quantitative-Trading-Strategy-Integrating-MACD-RSI-and-RVOL" (MACD, RSI, & RVOL Strategy (BobBarker42069)).

FMZ source id: 439081

Source
    https://www.fmz.com/strategy/439081 (PineScript v4, FMZ last modified 2024-01-17 15:50:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 259-288), RSI 14, 30 / 70; MACD 12 / 26 / 9; RVOL = volume / sma(volume, 14), 2 / 5
    (co and crossover(delta, 0)) or (co and crossover(RVOL, 2)) or (crossover(delta, 0) and crossover(RVOL, 2)) -> entry long
    (cu and crossunder(delta, 0)) or (cu and crossunder(RVOL, 5)) or (crossunder(delta, 0) and crossunder(RVOL, 5)) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI is Pine's (rma). Orders only once the RSI exists. When both sides signal on one bar the
      later call (short) wins. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, two-of-three RSI / MACD / relative-volume crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the relative volume volume / sma(volume, 14); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439081_rsi_macd_rvol_two_of_three_crossings_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rvol_up": [2.0, 1.5],
    "rsi_len": [14, 9],
}
DEFAULT_PARAMS = {"rsi_len": 14, "over_sold": 30.0, "over_bought": 70.0, "fast": 12, "slow": 26, "signal": 9,
                  "rvol_len": 14, "rvol_up": 2.0, "rvol_dn": 5.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _over(a, b):
    return (a > b) & (a.shift(1) <= (b.shift(1) if isinstance(b, pd.Series) else b))


def _under(a, b):
    return (a < b) & (a.shift(1) >= (b.shift(1) if isinstance(b, pd.Series) else b))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    av = v.rolling(int(p["rvol_len"])).mean()
    rvol = v / av.where(av != 0)
    co, cu = _over(r, float(p["over_sold"])), _under(r, float(p["over_bought"]))
    du, dd = _over(delta, 0.0), _under(delta, 0.0)
    vu, vd = _over(rvol, float(p["rvol_up"])), _under(rvol, float(p["rvol_dn"]))
    ok = r.notna()
    buy = ok & ((co & du) | (co & vu) | (du & vu))
    sell = ok & ((cu & dd) | (cu & vd) | (dd & vd))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (buy & ~sell).astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
