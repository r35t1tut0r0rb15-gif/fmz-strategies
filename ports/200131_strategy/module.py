"""N-bar log-return breakout of its own prior N-bar range; exit when it crosses back through its
N-bar mean ("simple volatility strategy").
Port of FMZ strategy #200131 "吕神-简易波动率策略" (Lü's simple volatility strategy, demo).

Source
    https://www.fmz.com/strategy/200131 (JavaScript, author "扁豆子", FMZ last modified
    2020-04-23 12:25:16). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 217-338), N 90
    once per new bar: vix = ln(Bar.Close) / ln(records[len-N].Close) - 1   (Bar = records[len-1])
    vix_ma = TA.MA(vix_arr, N); vix_up = TA.Highest(vix_arr, N); vix_dw = TA.Lowest(vix_arr, N)
    flat:  vix crosses above vix_up -> buy;  vix crosses below vix_dw -> sell short
    long:  vix crosses below vix_ma -> close;  short: vix crosses above vix_ma -> close

Interpretation choices
    * Criterion 2: ln(C_t)/ln(C_{t-N+1}) - 1 = log return / ln(price level). Dividing by
      ln(price) makes the value depend on the price scale and breaks for prices near or below 1
      (FX pairs). The port uses the log return ln(C_t/C_{t-N+1}) itself; for BTC (ln price ~ 9,
      nearly constant over a window) the two give the same crosses up to a slowly varying scale.
    * Bars: the bot reads the forming bar once per new bar (records[-1] -> completed bar t).
      TA.Highest/Lowest exclude the current element (SURVEY_README FMZ TA rule), so the range is
      vix[t-N..t-1]; the MA includes t.
    * The bot exits on one poll and, flat on the next poll of the same bar, may open the opposite
      side if that bar also crosses the opposite band: REVERSAL INTENDED for that case (exit and
      opposite entry on the same bar; portfolio_kwargs {}). Otherwise entries only from flat.
    * FREQ = "15min" from the backtest header. XBTUSD contract and Amount: original_sizing.txt.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_200131_log_return_range_breakout"
FAMILY = "momentum_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [45, 90, 180],
}
DEFAULT_PARAMS = {"n": 90}


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
    n = int(p["n"])
    lc = np.log(bars_df["close"])
    vix = lc - lc.shift(n - 1)
    ma = vix.rolling(n).mean()
    up = vix.rolling(n).max().shift(1)
    dw = vix.rolling(n).min().shift(1)
    long_in = ((vix > up) & (vix.shift(1) <= up.shift(1))).to_numpy()
    short_in = ((vix < dw) & (vix.shift(1) >= dw.shift(1))).to_numpy()
    long_out = ((vix < ma) & (vix.shift(1) >= ma.shift(1))).to_numpy()
    short_out = ((vix > ma) & (vix.shift(1) <= ma.shift(1))).to_numpy()

    m = len(bars_df)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        if pos == 1 and long_out[i]:
            lx[i], pos = True, 0
        elif pos == -1 and short_out[i]:
            sx[i], pos = True, 0
        if pos == 0:
            if long_in[i]:
                le[i], pos = True, 1
            elif short_in[i]:
                se[i], pos = True, -1

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
