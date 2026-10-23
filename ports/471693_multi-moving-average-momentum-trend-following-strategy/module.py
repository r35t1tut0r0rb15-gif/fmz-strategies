"""Broker days, long only: above the SMA 150 with at least 5 up days out of the last 10 (one of them on volume above the 20-day volume average), an RSI condition, the SMA 50 above the SMA 150 and rising on 25 of the last 40 days, rising SMA 150 and SMA 200 and no close under the SMA 150 in the last 40 days, it goes long; the long closes when the close is not above the SMA 150 and the SMA 50 is under the SMA 150 (or on a run of high-volume down days).
Port of FMZ strategy #471693 "Multi Moving Average Momentum Trend Following Strategy" (Micho's 150 (1D Time Frame Only)).

FMZ source id: 471693

Source
    https://www.fmz.com/strategy/471693 (PineScript v5, FMZ last modified 2024-11-12 15:05:09).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 159-274), SMA 20 / 50 / 150 / 200; volume SMA 20; RSI 14 and its SMA 14; 10-day candle counts; 40-day checks
    buyCondition = close > sma150 and buyerDays > 4 and highVolumeDays >= 1 and rsiCondition and sma50 > sma150 and sma50Rising and sma150Rising and sma200Rising and priceAboveSma150 -> entry Buy
    sellCondition = priceBelowSma150 and (sma50 < sma150 or (sellerDays > 5 and highSellerVolumeDays >= 5)) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The candle counts look at the last 10 days (bar 0 to 9), each day's volume against TODAY's volume
      average. rsiCondition = RSI >= 55 or (SMA 14 of RSI > 50 and RSI rising). sma50Rising counts days
      1 to 40 back where the SMA 50 rose, needing 25. priceAboveSma150 fails only on a known close under a
      known SMA 150 in days 1 to 40 (an na comparison is false, so missing history passes, as written);
      priceBelowSma150 likewise holds when the SMA 150 is not yet known. The "SMA 150 above SMA 200"
      check is computed but unused. A buy and a sell can never meet on one bar. Long only. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute; the
      timeframe.isdaily guard holds. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Minervini-style trend template with candle and volume counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20 in the up- / down-day counts; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471693_sma150_trend_template_volume_days_long_only"
FAMILY = "trend_template"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "check_len": [40, 20],
    "rising_need": [25, 15],
}
DEFAULT_PARAMS = {"check_len": 40, "rising_need": 25}


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
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    s50, s150, s200 = (c.rolling(n).mean() for n in (50, 150, 200))
    vma = v.rolling(20).mean()
    r = _rsi(c, 14)
    rsi_ok = (r >= 55) | ((r.rolling(14).mean() > 50) & (r > r.shift(1)))
    zero = pd.Series(0, index=c.index)
    up_d, up_v, dn_d, dn_v = zero.copy(), zero.copy(), zero.copy(), zero.copy()
    for i in range(10):
        ci, oi, vi = c.shift(i), o.shift(i), v.shift(i)
        up_d += (ci > oi).astype(int)
        up_v += ((ci > oi) & (vi > vma)).astype(int)
        dn_d += (ci < oi).astype(int)
        dn_v += ((ci < oi) & (vi > vma)).astype(int)
    k = int(p["check_len"])
    rising, below = zero.copy(), pd.Series(False, index=c.index)
    for i in range(1, k + 1):
        rising += (s50.shift(i) > s50.shift(i + 1)).astype(int)
        below |= c.shift(i) < s150.shift(i)
    buy = ((c > s150) & (up_d > 4) & (up_v >= 1) & rsi_ok & (s50 > s150) & (rising >= int(p["rising_need"]))
           & (s150 > s150.shift(1)) & (s200 > s200.shift(1)) & ~below)
    sell = ~(c > s150) & ((s50 < s150) | ((dn_d > 5) & (dn_v >= 5)))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), sell.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
