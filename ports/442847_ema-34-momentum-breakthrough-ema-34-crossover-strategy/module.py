"""Close crossing EMA 34 bands of the highs and lows, 1-hour bars: the close crossing over the EMA of highs goes long, under the EMA of lows goes short; a close 50 price units past the latest signal close
(re-expressed as a fraction) takes the profit; reversing.
Port of FMZ strategy #442847 "动量突破EMA-34交叉策略Momentum-Breakthrough-EMA-34-Crossover-Strategy" (EMA 34 Crossover Strategy_4).

FMZ source id: 442847

Source
    https://www.fmz.com/strategy/442847 (PineScript v5, FMZ last modified 2024-02-26 15:05:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-149), EMA 34 of close / high / low; exit points 50 (price units)
    crossover(close, emaHigh) -> push close, entry Buy;  crossunder(close, emaLow) -> push close, entry Sell
    exitLong = close >= last pushed close + 50 -> close Buy;  exitShort = close <= last pushed close - 50 -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit tests read the latest pushed signal close (either side) before this bar's push. Criterion
      2: the 50-unit distance is in price units: as a fraction of the close at the BTC reading of
      42000, 0.00119 x that close. The tests run at the bar close; each close acts only on a held
      position. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit target -> fraction of the signal close.
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

NAME = "fmz_442847_ema34_high_low_band_cross_unit_target"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [34, 20],
    "exit_frac": [0.00119, 0.01],
}
DEFAULT_PARAMS = {"length": 34, "exit_frac": 0.00119}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    eh = h.ewm(span=n, adjust=False).mean()
    el = lo.ewm(span=n, adjust=False).mean()
    lg = ((c > eh) & (c.shift(1) <= eh.shift(1))).to_numpy()
    sh = ((c < el) & (c.shift(1) >= el.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    f = float(p["exit_frac"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held, last = 0, np.nan
    for i in range(m):
        xl = (not np.isnan(last)) and cv[i] >= last * (1 + f)
        xs = (not np.isnan(last)) and cv[i] <= last * (1 - f)
        new = held
        if lg[i]:
            last = cv[i]
            if new != 1:
                new = 1
        if sh[i]:
            last = cv[i]
            if new != -1:
                new = -1
        if xl and held == 1 and new == 1:
            new = 0
        if xs and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
