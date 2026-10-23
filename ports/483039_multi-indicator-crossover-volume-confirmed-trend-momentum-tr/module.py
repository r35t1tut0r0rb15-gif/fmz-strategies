"""Broker days: a MACD bullish crossing with RSI 14 over 50, the stochastic RSI (14, 3, 3) %K above %D and volume over 1.5 x its 14-day average goes long; the mirror goes short; the opposite signal reverses.
Port of FMZ strategy #483039 "Multi Indicator Crossover Volume Confirmed Trend Momentum Trading Strategy" (BTCUSDT Strategy with Volume, MACD, RSI, StochRSI).

FMZ source id: 483039

Source
    https://www.fmz.com/strategy/483039 (PineScript v5, FMZ last modified 2025-02-21 10:34:52).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 139-179), MACD 12 / 26 / 9; RSI 14; StochRSI 14 / 3 / 3; volume SMA 14 x 1.5
    longCondition = crossover(macd, signal) and rsi > 50 and stochK > stochD and volume > sma(volume, 14) x 1.5 -> entry Long;  shortCondition mirrored -> entry Short
    stochRsi = ta.stoch(rsi, rsi, rsi, 14);  K = sma(stochRsi, 3);  D = sma(K, 3)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stoch(rsi, rsi, rsi, 14) is the stochastic of the RSI over its own 14-bar range (its division
      by zero is na). Entries only; an opposite entry reverses. The title names BTCUSDT; the header is
      ETH_USDT; the rules are generic. REVERSAL INTENDED. 10 % of equity is sizing. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings confirmed by RSI, stochastic RSI and a volume spike.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.5 x its SMA 14; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483039_macd_cross_rsi_stochrsi_volume_spike_reversal"
FAMILY = "macd"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_mult": [1.5, 1.0],
    "stoch_len": [14, 21],
}
DEFAULT_PARAMS = {"vol_mult": 1.5, "stoch_len": 14}


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
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, 14)
    n = int(p["stoch_len"])
    lo_r, hi_r = r.rolling(n).min(), r.rolling(n).max()
    st = 100 * (r - lo_r) / (hi_r - lo_r).where(hi_r != lo_r)
    k = st.rolling(3).mean()
    d = k.rolling(3).mean()
    spike = v > v.rolling(14).mean() * float(p["vol_mult"])
    buy = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (r > 50) & (k > d) & spike
    sell = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (r < 50) & (k < d) & spike
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
