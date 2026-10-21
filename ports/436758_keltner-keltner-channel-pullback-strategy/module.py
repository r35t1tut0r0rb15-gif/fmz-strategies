"""Keltner band bounce with a tick stop, 1-hour bars: the close crossing back up over the lower band (SMA 200 minus 8 ATR 200) goes long, crossing back down under the upper band goes short, reversing; each trade
has a 50-tick stop re-expressed as an ATR multiple.
Port of FMZ strategy #436758 "Keltner通道突破回抽策略Keltner-Channel-Pullback-Strategy" (Keltner border bounce).

FMZ source id: 436758

Source
    https://www.fmz.com/strategy/436758 (PineScript v2, FMZ last modified 2023-12-27 14:49:39).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 118-162), length 200, ATR 200, width 8 ATR, close on mid-line touch off, enter from inside off, stop 50 ticks
    EMA = sma(close, 200) (named EMA);  top / bottom = EMA +- 8 atr(200);  buyEntry = crossover(close, bottom) -> entry BUY;  sellEntry = crossunder(close, top) -> entry SELL
    exit(loss = 50) for BUY and SELL;  (off by default: close on a mid-line crossing; entries on a touch from inside)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 50-tick stop is re-expressed as sl_stop = k_atr x ATR(200) / close of the signal bar
      (the script's own ATR), shifted one bar inside stops() (re-based on the fill); 0.035 is the reading
      (about 50 ticks of 0.1 on BTC against a 1-hour ATR near 150), 1.0 one ATR. The "EMA" is an SMA as
      written. The two switches are off by default and not ported (the inside-touch branch would even send
      a long entry named SELL). REVERSAL INTENDED. The trade size input is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: ADAPT, tick stop -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the trade size and the tick stop input stored.
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

NAME = "fmz_436758_keltner_border_bounce_stop"
FAMILY = "mean_reversion"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_dev": [8.0, 6.0],
    "k_atr": [0.035, 1.0],
}
DEFAULT_PARAMS = {"length": 200, "atr_len": 200, "k_dev": 8.0, "k_atr": 0.035}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mid = c.rolling(int(p["length"])).mean()
    atr = _atr(bars_df, p["atr_len"])
    top = mid + float(p["k_dev"]) * atr
    bot = mid - float(p["k_dev"]) * atr
    buy = (c > bot) & (c.shift(1) <= bot.shift(1))
    sell = (c < top) & (c.shift(1) >= top.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["k_atr"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1)}


def portfolio_kwargs(**params):
    return {}
