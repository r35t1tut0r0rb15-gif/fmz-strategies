"""Ichimoku 22 / 60 / 120 trend with an RSI and a candle-body volatility filter, 3-minute bars: with the tenkan above the
kijun, a positive 29-bar momentum, the close above the cloud of 29 bars ago, RSI 14 above 50 and the 2-bar average body
above 0.2 % of the price, the strategy goes long; the mirror (with the source's "rs < 50" test) goes short. Always in
after the first signal.
Port of FMZ strategy #433104 "Ichimoku-Kinko-Hyo趋势跟踪策略Ichimoku-Kinko-Hyo-indicator-Balancing-Trend-Strategy" (Ichimoku Kinko Hyo: ETH 3h Strategy by tobuno).

FMZ source id: 433104

Source
    https://www.fmz.com/strategy/433104 (PineScript v4, FMZ last modified 2023-11-24 14:38:47).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 173-252), tenkan 22, kijun 60, span B 120, chikou / senkou offsets 30; vol length 2, target 0.2 %; longs and shorts on
    bullish = tenkan > kijun and mom(close, 29) > 0 and close > max(spanA, spanB)[29] and rsi > 50 and sma(|close - open| / mid x 100, 2) > 0.2
    bearish = tenkan < kijun and mom(close, 29) < 0 and close < min(spanA, spanB)[29] and rs < 50 and the same volatility
    entry long when bullish;  entry short when bearish;  the closes apply only when a side is disabled

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the bearish RSI test reads rs (the gain / loss ratio) < 50, nearly always true. RSI
      uses rma(gain, 14) / rma(loss, 14). The cloud and momentum use the offsets minus one (29).
    * The entries are levels: a repeated entry is ignored (pyramiding 1); strategy.entry reverses:
      REVERSAL INTENDED. The title's "3h" is not the header's period: FREQ = "3min" from the backtest
      header. The date window is always true.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku lines, momentum sign, RSI and a percent body filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_433104_ichimoku_rsi_body_filter"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_target": [0.2, 0.1],
    "offset": [30, 26],
}
DEFAULT_PARAMS = {"ts_bars": 22, "ks_bars": 60, "ssb_bars": 120, "offset": 30, "vol_len": 2, "vol_target": 0.2,
                  "rsi_len": 14}


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

    def mid(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    ten, kij = mid(p["ts_bars"]), mid(p["ks_bars"])
    sa, sb = (ten + kij) / 2, mid(p["ssb_bars"])
    k = int(p["offset"]) - 1
    ss_hi = pd.concat([sa.shift(k), sb.shift(k)], axis=1).max(axis=1, skipna=False)
    ss_lo = pd.concat([sa.shift(k), sb.shift(k)], axis=1).min(axis=1, skipna=False)
    mom = c - c.shift(k)
    ch = c.diff()
    n = int(p["rsi_len"])
    ag = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    al = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = ag / al
    rsi = 100 - 100 / (1 + rs)
    diff = ((c - o) / ((c + o) / 2) * 100).abs()
    hv = diff.rolling(int(p["vol_len"])).mean() > float(p["vol_target"])
    bull = ((ten > kij) & (mom > 0) & (c > ss_hi) & (rsi > 50) & hv).to_numpy()
    bear = ((ten < kij) & (mom < 0) & (c < ss_lo) & (rs < 50) & hv).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if bull[i]:
            pos = 1
        elif bear[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
