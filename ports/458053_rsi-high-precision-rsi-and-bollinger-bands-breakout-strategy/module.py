"""Hourly bars: RSI 14 under 30 with the close under the lower Bollinger band (20, 2) on above-average volume goes long; RSI over 70 above the upper band on above-average volume goes short; each with a stop 1 ATR 14 and a target 5 ATR from the signal close; reversing.
Port of FMZ strategy #458053 "高精度RSI和布林带突破策略与优化风险比-High-Precision-RSI-and-Bollinger-Bands-Breakout-Strategy-with-Optimized-Risk-Reward-Ratio" (Estratégia de Alta Acertividade com R/R 1:5).

FMZ source id: 458053

Source
    https://www.fmz.com/strategy/458053 (PineScript v5, FMZ last modified 2024-07-29 15:38:55).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 188-230), RSI 14, 70 / 30; BB 20 x 2; volume SMA 20; ATR 14; TP 5 x ATR, SL 1 x ATR
    buy_condition = rsi < 30 and close < lower_bb and volume > sma(volume, 20) -> entry Compra, exit("Take Profit/Stop Loss", limit = close + 5 atr, stop = close - atr)
    sell_condition = rsi > 70 and close > upper_bb and volume > avg -> entry Venda, exit("Take Profit/Stop Loss", limit = close - 5 atr, stop = close + atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on signal bars, as levels from that close and ATR: ported as fractions of the
      fill, exact (1e-6 floor). Both sides use one exit id, but the calls only happen on their own signal
      bars, so each trade keeps its own bracket until the opposite entry reverses it. A repeated signal
      while in the position re-sends the bracket from the new bar (not followed). Pine's stdev is the
      population deviation. REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver
      D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, RSI / Bollinger extremes on above-average volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458053_rsi_bollinger_extreme_volume_atr_1_5_bracket_1h_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_ratio": [5.0, 2.0],
    "sl_ratio": [1.0, 1.5],
}
DEFAULT_PARAMS = {"rsi_len": 14, "ob": 70.0, "os": 30.0, "bb_len": 20, "bb_dev": 2.0, "tp_ratio": 5.0, "sl_ratio": 1.0}


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
    c, v = bars_df["close"], bars_df["volume"]
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_dev"]) * c.rolling(n).std(ddof=0)
    vol_ok = v > v.rolling(20).mean()
    buy = (r < float(p["os"])) & (c < basis - dev) & vol_ok
    sell = (r > float(p["ob"])) & (c > basis + dev) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, 14)
    tp_d, sl_d = float(p["tp_ratio"]) * atr, float(p["sl_ratio"]) * atr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
