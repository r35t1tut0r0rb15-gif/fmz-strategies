"""An EMA 21 / 55 MACD rising (falling) for two bars with the VWMA 55 on the far side of the VWMA 144, a fast stochastic 8 above (below) its SMA 5 and a stochastic RSI 8 / 21 under 30 (over 70), broker days: the rising set goes long, the falling set goes short; reversing.
Port of FMZ strategy #427574 "Hawk Eye Short term Trading Strategy" (Hawk 1H Strategy).

FMZ source id: 427574

Source
    https://www.fmz.com/strategy/427574 (PineScript v3, FMZ last modified 2023-09-22 12:09:01).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 136-168), MACD EMA 21 / 55; stoch 8, SMA 5; stoch RSI 8 / 21, K 5; VWMA 55 / 144
    MACD > MACD[1] > MACD[2] and vwma(55) < vwma(144) and stoch(8) > sma(stoch, 5) and k < 30 -> entry MacdLE
    MACD < MACD[1] < MACD[2] and vwma(55) > vwma(144) and stoch(8) < sma(stoch, 5) and k > 70 -> entry MacdSE

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long side needs the VWMA 55 UNDER the VWMA 144 (a rising MACD in a falling VWMA order), as
      written. k is the SMA 5 of the stochastic of RSI 8 over 21 bars. The title says 1H; the backtest
      header says 1d and wins (rule 1). REVERSAL INTENDED. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD momentum with VWMA order and stochastic filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in vwma(close, 55) and vwma(close, 144); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427574_ema21_55_macd_rise_vwma55_144_stoch_rsi_reversal"
FAMILY = "macd_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [21, 12],
    "slow_length": [55, 26],
}
DEFAULT_PARAMS = {"fast_length": 21, "slow_length": 55, "length_rsi": 8, "length_stoch": 21, "smooth_k": 5}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _stoch(src, hi, lo, n):
    ll, hh = lo.rolling(n).min(), hi.rolling(n).max()
    return 100 * (src - ll) / (hh - ll).replace(0.0, np.nan)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    macd = c.ewm(span=int(p["fast_length"]), adjust=False).mean() - c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    vf = _stoch(c, h, lo, 8)
    vs = vf.rolling(5).mean()
    r = _rsi(c, int(p["length_rsi"]))
    k = _stoch(r, r, r, int(p["length_stoch"])).rolling(int(p["smooth_k"])).mean()
    w55 = (c * v).rolling(55).sum() / v.rolling(55).sum()
    w144 = (c * v).rolling(144).sum() / v.rolling(144).sum()
    m1, m2 = macd.shift(1), macd.shift(2)
    le = (macd > m1) & (m1 > m2) & (w55 < w144) & (vf > vs) & (k < 30)
    se = (macd < m1) & (m1 < m2) & (w55 > w144) & (vf < vs) & (k > 70)
    false = pd.Series(False, index=c.index)
    return le, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
