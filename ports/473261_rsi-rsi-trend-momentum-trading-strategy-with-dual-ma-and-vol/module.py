"""Broker days, long only: RSI 10 at or under 30 with the SMA 250 above the SMA 500 on volume over 2.5 x its 20-bar average goes long; the long closes when the SMA 250 crosses under the SMA 500, with a 5 % stop from the fill.
Port of FMZ strategy #473261 "RSI趋势动量交易策略结合双均线和成交量确认-RSI-Trend-Momentum-Trading-Strategy-with-Dual-MA-and-Volume-Confirmation" (Rsi Long-Term Strategy [15min]).

FMZ source id: 473261

Source
    https://www.fmz.com/strategy/473261 (PineScript v5, FMZ last modified 2024-11-28 17:02:32).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 102-159), RSI 10 <= 30; SMA 250 / 500; volume SMA 20 x 2.5; stop 5 % (ticks of the average price)
    Long_cond = rsi_overs and SMA1 > SMA2 and Volume_condt -> entry Long;  crossunder(SMA1, SMA2) -> close Long
    pera(5) = round(5 / 100 x position_avg_price / mintick) when in a position -> exit('SL', loss = los)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is 5 % of the average entry price (the fill): sl_stop 0.05. Stated approximation: the
      source sends it from the fill bar's close (so it acts from the next bar), the house from the fill
      (as #429494); the tick rounding is dropped. The entry is a state, so after a stop the strategy
      re-enters on the next qualifying bar. The title says 15 minutes; the header is 1 day. Long only.
      100 % of equity and the commission are sizing and costs. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 1-day bars: coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 5 % stop from the fill.
    2 generic: PASS, oversold RSI in a long-term uptrend on a volume spike.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital and commission stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 2.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473261_rsi10_oversold_sma250_500_volume_spike_5pct_stop_long_only"
FAMILY = "rsi_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_os": [30.0, 25.0],
    "sl": [0.05, 0.08],
}
DEFAULT_PARAMS = {"rsi_len": 10, "rsi_os": 30.0, "fast": 250, "slow": 500, "vol_mult": 2.5, "sl": 0.05}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    r = _rsi(c, int(p["rsi_len"]))
    s1, s2 = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    vol_ok = v > v.rolling(20).mean() * float(p["vol_mult"])
    entry = (r <= float(p["rsi_os"])) & (s1 > s2) & vol_ok
    ex = (s1 < s2) & (s1.shift(1) >= s2.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return entry.astype(bool), ex.astype(bool), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}
