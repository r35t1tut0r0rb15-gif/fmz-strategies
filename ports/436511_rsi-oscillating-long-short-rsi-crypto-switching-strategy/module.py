"""Ichimoku alignment on Heikin-Ashi closes with an RSI test, 3-minute bars: Tenkan over Kijun, the Heikin-Ashi close over its close 29 bars ago and over the cloud of 29 bars ago, and an RSI over 50 goes long;
the mirror (Tenkan under Kijun, momentum down, under the cloud, and "rs" under 50) goes short; reversing.
Port of FMZ strategy #436511 "震荡多空RSI换币策略Oscillating-Long-Short-RSI-Crypto-Switching-Strategy" (Ichimoku + RSI Crypto trending strategy).

FMZ source id: 436511

Source
    https://www.fmz.com/strategy/436511 (PineScript v4, FMZ last modified 2023-12-25 13:49:48).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 210-298), Tenkan 20, Kijun 50, Senkou B 120, offsets 30, Heikin-Ashi on
    tenkan, kijun, senkouB = (lowest + highest) / 2 over 20 / 50 / 120 plain bars;  senkouA = avg(tenkan, kijun);  ss_high / ss_low = max / min of senkouA and senkouB 29 bars back
    bullish = tenkan > kijun and mom(haClose, 29) > 0 and haClose > ss_high and rsi > 50;  bearish = tenkan < kijun and mom(haClose, 29) < 0 and haClose < ss_low and rs < 50;  entry Long when bullish, Short when bearish

Interpretation choices (Pine rules in SURVEY_README.md)
    * haClose is the Heikin-Ashi close of the same bars (the security call on the same timeframe);
      the Ichimoku levels use the plain highs and lows. The bearish RSI test reads rs (the gain /
      loss ratio) under 50, as written (it is nearly always true). The long and short close rules
      use switches that are on, so they never fire. REVERSAL INTENDED. The percent-of-equity size is
      sizing. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, Ichimoku on Heikin-Ashi closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436511_ichimoku_ha_rsi"
FAMILY = "ichimoku"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ts_bars": [20, 10],
    "ks_bars": [50, 30],
}
DEFAULT_PARAMS = {"ts_bars": 20, "ks_bars": 50, "ssb_bars": 120, "cs_offset": 30, "ss_offset": 30}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ha_close = (o + h + lo + c) / 4
    hc = ha_close.to_numpy()
    o_, c_ = o.to_numpy(), c.to_numpy()
    ha_open = np.empty(len(hc))
    for i in range(len(hc)):
        ha_open[i] = (o_[0] + c_[0]) / 2 if i == 0 else (ha_open[i - 1] + hc[i - 1]) / 2

    def middle(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    tenkan, kijun = middle(p["ts_bars"]), middle(p["ks_bars"])
    senkou_a, senkou_b = (tenkan + kijun) / 2, middle(p["ssb_bars"])
    k = int(p["ss_offset"]) - 1
    ss_high = np.maximum(senkou_a.shift(k), senkou_b.shift(k))
    ss_low = np.minimum(senkou_a.shift(k), senkou_b.shift(k))
    hcs = ha_close
    ch = hcs.diff()
    gain, loss = ch.clip(lower=0), (-ch).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = avg_gain / avg_loss
        rsi = 100 - 100 / (1 + rs)
    mom = hcs.diff(int(p["cs_offset"]) - 1)
    bull = (tenkan > kijun) & (mom > 0) & (hcs > ss_high) & (rsi > 50)
    bear = (tenkan < kijun) & (mom < 0) & (hcs < ss_low) & (rs < 50)
    false = pd.Series(False, index=bars_df.index)
    return bull.fillna(False).astype(bool), false, bear.fillna(False).astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
