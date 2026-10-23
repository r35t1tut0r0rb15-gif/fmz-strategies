"""Hourly bars: a close under the lower Bollinger band (20, 2) with RSI 14 under 30, volume over 1.5 x its 20-bar average, ATR 14 under 3 % of the close and the close not below the last completed day's SMA 20 goes long; the mirror at the upper band goes short; a close back over the SMA 20, RSI over 60 or a close 5 % under the lower band closes a long (mirrored for a short); reversing.
Port of FMZ strategy #489160 "Multi Timeframe Adaptive Mean Reversion with Volume Analysis Strategy" (Multi-Timeframe Adaptive Mean Reversion with Volume Analysis Strategy).

FMZ source id: 489160

Source
    https://www.fmz.com/strategy/489160 (PineScript v5, FMZ last modified 2025-04-02 11:39:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 187-277), BB 20 x 2; RSI 14 (30 / 70, "adaptive" by floor(10 x ATR / close)); volume / SMA 20 > 1.5; ATR 14 / close < 0.03; daily ("D") SMA 20 trend; exits SMA 20, RSI 60 / 40, band x 0.95 / 1.05
    long_condition = close < lower and rsi < min(30, 30 + floor(10 natr)) and vol_ratio > 1.5 and higher_trend >= 0 and natr < 0.03 -> entry Long;  short_condition mirrored (higher_trend <= 0) -> entry Short
    exit_long = close > sma or rsi > 60 or close < lower x 0.95 -> close Long;  exit_short = close < sma or rsi < 40 or close > upper x 1.05 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily SMA is security("D", ...) without lookahead: the port uses the last completed broker day
      (as #438014). higher_trend is 0 when the daily SMA is na, so both sides pass then. Under the
      volatility filter floor(10 x ATR / close) is 0, so the "adaptive" RSI levels are 30 / 70; the daily
      RSI is computed but unused. The closes act only on a position the bar's entries leave unchanged; an
      opposite entry reverses. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger mean reversion on volume, filtered by the daily trend and volatility.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: daily SMA 20 of the last completed broker day (17:00 America/New_York); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489160_bollinger_mean_reversion_volume_daily_sma_trend_1h_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_mult": [2.0, 2.5],
    "vol_threshold": [1.5, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "bb_mult": 2.0, "vol_threshold": 1.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n = int(p["length"])
    sma = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    up_b, lo_b = sma + dev, sma - dev
    r = _rsi(c, 14)
    vr = v / v.rolling(n).mean()
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    natr = atr / c
    day = broker_day(c.index)
    dsma = c.groupby(day).last().rolling(n).mean().shift(1)      # the last COMPLETED broker day
    hs = pd.Series(dsma.reindex(day).to_numpy(), index=c.index)
    trend = pd.Series(np.where(c > hs, 1, np.where(c < hs, -1, 0)), index=c.index)
    adj = np.floor(10 * natr)
    os_lvl = np.minimum(30.0, 30 + adj)
    ob_lvl = np.maximum(70.0, 70 - adj)
    vt = float(p["vol_threshold"])
    calm = natr < 0.03
    buy = ((c < lo_b) & (r < os_lvl) & (vr > vt) & (trend >= 0) & calm).to_numpy()
    sell = ((c > up_b) & (r > ob_lvl) & (vr > vt) & (trend <= 0) & calm).to_numpy()
    ex_l = ((c > sma) | (r > 60) | (c < lo_b * 0.95)).to_numpy()
    ex_s = ((c < sma) | (r < 40) | (c > up_b * 1.05)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and ex_l[i]:
                new = 0
            elif pos == -1 and ex_s[i]:
                new = 0
        if new != pos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
