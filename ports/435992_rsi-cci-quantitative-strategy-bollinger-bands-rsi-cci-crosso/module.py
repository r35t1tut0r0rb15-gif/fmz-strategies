"""Three-oscillator extremes with a take profit, 1-hour bars: a close under the lower Bollinger band with the RSI 14 under 33 and the CCI 20 under -215 goes
long; the mirror (RSI over 70, CCI over 250) goes short (reversing); each trade has a 600-tick take profit re-expressed as an ATR multiple.
Port of FMZ strategy #435992 "布林带RSI指标的CCI均线交叉策略Quantitative-Strategy-Bollinger-Bands-RSI-CCI-Crossover-Strategy" (Bollinger Bands (BB RSI CCI)).

FMZ source id: 435992

Source
    https://www.fmz.com/strategy/435992 (PineScript v5, FMZ last modified 2023-12-20 16:24:49).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 139-209), Bollinger 20 / 2 sd; RSI 14; CCI 20 (mean deviation); take profit 600 ticks
    longCBB = close < lower;  longBRSI = rsi < 33;  longcci = cci < -215;  shortCBB = close > upper;  shortBRSI = rsi > 70;  shortcci = cci > 250
    entry long (all three);  entry short (all three);  exit(profit = 600) for the open position

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the take profit is 600 ticks (60 USD on BTC at a 0.1 tick); the port uses tp_stop =
      k_atr x ATR / close of the signal bar, shifted one bar inside stops() (re-based on the fill); no
      stop exists in the script. The CCI uses the mean absolute deviation (Pine's dev). The smoothing
      line and the RSI average are only drawn. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-hour bars: not coarse. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry.
    2 generic: ADAPT, tick target -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick take-profit input quoted in original_sizing.txt.
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

NAME = "fmz_435992_bollinger_rsi_cci_extremes_tp"
FAMILY = "mean_reversion"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.2, 1.0],
    "length": [20, 30],
}
DEFAULT_PARAMS = {"k_atr": 0.2, "length": 20, "mult": 2.0, "rsi_len": 14, "atr_len": 14}


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
    c = bars_df["close"]
    n = int(p["length"])
    ma = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = ma + dev, ma - dev
    r = int(p["rsi_len"])
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / r, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / r, adjust=False).mean()
    rsi = pd.Series(np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn))), index=c.index)
    md = c.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        cci = (c - ma) / (0.015 * md)
    le = ((c < lower) & (rsi < 33) & (cci < -215)).fillna(False).astype(bool)
    se = ((c > upper) & (rsi > 70) & (cci > 250)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["k_atr"])).shift(1)
    return {"tp_stop": f}


def portfolio_kwargs(**params):
    return {}
