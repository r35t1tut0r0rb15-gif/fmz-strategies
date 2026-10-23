"""Hourly bars, long only: RSI 14 under 30 under the lower Bollinger band, or a positive MACD histogram in an SMA 50 > 200 trend with a close above the previous 10-bar high, or a 1.5x volume spike above the upper band (all with the close above the 50-bar low) goes long; the mirror set (below the 50-bar high) closes it.
Port of FMZ strategy #454356 "基于RSIMACD布林带和成交量的混合交易策略RSI-MACD-Bollinger-Bands-and-Volume-Based-Hybrid-Trading-Strategy" (Optimize Edilmiş Kapsamlı Ticaret Stratejisi (liquidity zones, 30 minutes)).

FMZ source id: 454356

Source
    https://www.fmz.com/strategy/454356 (PineScript v5, FMZ last modified 2024-06-17 15:54:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 109-186), RSI 14; MACD 12 / 26 / 9; BB 20 x 2; volume spike 1.5 x SMA 20; SMA 50 / 200; liquidity zone 50
    buySignal = (rsi < 30 and close < lowerBand and close > lowest(low, 50)) or (macdHist > 0 and trendUp and close > highest(high, 10)[1] and close > liqLow) or (volumeSpike and close > upperBand and close > liqLow)
    buySignal and (not inPosition or not isBuy) -> entry Buy;  sellSignal and inPosition and isBuy -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags make it a plain long / flat toggle. The 50-bar low includes the current bar, so
      close > liquidityZoneLow only fails when the close is the window's low. barstate.isconfirmed is true
      on every historical bar. Pine's stdev is the population deviation. Long only. 10 % of equity is
      sizing. FREQ = "1h" from the backtest header (the title says 30 minutes).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, three alternative oversold / breakout / volume-spike entries with mirrored exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 10 % of equity, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 20 (the volume spike); exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454356_rsi_macd_bb_volume_spike_liquidity_zone_1h_long_only"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "spike": [1.5, 2.0],
    "zone": [50, 100],
}
DEFAULT_PARAMS = {"spike": 1.5, "zone": 50}


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
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    rsi = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    basis = c.rolling(20).mean()
    dev = 2.0 * c.rolling(20).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    spike = v > v.rolling(20).mean() * float(p["spike"])
    s50, s200 = c.rolling(50).mean(), c.rolling(200).mean()
    z = int(p["zone"])
    zh, zl = h.rolling(z).max(), lo.rolling(z).min()
    buy = (((rsi < 30) & (c < lower) & (c > zl)) | ((hist > 0) & (s50 > s200) & (c > h.rolling(10).max().shift(1)) & (c > zl))
           | (spike & (c > upper) & (c > zl))).to_numpy()
    sell = (((rsi > 70) & (c > upper) & (c < zh)) | ((hist < 0) & (s50 < s200) & (c < lo.rolling(10).min().shift(1)) & (c < zh))
            | (spike & (c < lower) & (c < zh))).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if buy[i] and pos == 0:
            le[i], pos = True, 1
        elif sell[i] and pos == 1:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
