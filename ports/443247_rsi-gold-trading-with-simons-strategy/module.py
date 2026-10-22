"""SMA 21 / 200 crossings with an engulfing bar and RSI filter, 1-minute bars: a cross up on a bullish engulfing bar above the SMA 21 / 50 with the RSI under 70 goes long with a 4 % target and 1 % stop;
the mirror short, whose levels sit on the wrong side of the market, closes after its first bar; reversing.
Port of FMZ strategy #443247 "黄金复合移动平均线交叉RSI混入策略Gold-Trading-with-Simons-Strategy" (Gold Trading with Simons Strategy).

FMZ source id: 443247

Source
    https://www.fmz.com/strategy/443247 (PineScript v4, FMZ last modified 2024-03-01 12:28:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-227), SMA 21 / 50 / 200; RSI 14 (70 / 30); take profit 4 %, stop loss 1 % (the long's formulas used for both sides)
    long = crossover(ma21, ma200) and close > ma21 and close > ma50 and rsi < 70 and bullish engulfing -> entry Long, exit(limit = close x 1.04), exit(stop = close x 0.99)
    short = crossunder and close < ma21, ma50 and rsi > 30 and bearish engulfing -> entry Short, exit(limit = close x 1.04), exit(stop = close x 0.99)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long's bracket is fixed on the signal bar: fixed fractions 0.04 / 0.01 of the fill (#437751).
      The short reuses the long's formulas: a buy limit over and a buy stop under the price, both on
      the wrong side of the market, so the short closes at the first open after its fill bar (as
      #439872: the port closes it on that bar's signal). The "Stop Loss %" table value true is the 1
      default. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; long bracket fixed at entry; the short's wrong-side levels read as a close.
    2 generic: PASS, SMA crossings with an engulfing bar.
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

NAME = "fmz_443247_sma21_200_cross_engulfing_long_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length21": [21, 10],
    "length200": [200, 100],
}
DEFAULT_PARAMS = {"length21": 21, "length200": 200, "length50": 50, "rsi_len": 14, "tp_pct": 0.04, "sl_pct": 0.01}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _run(bars_df, p):
    o, c = bars_df["open"], bars_df["close"]
    m21 = c.rolling(int(p["length21"])).mean()
    m50 = c.rolling(int(p["length50"])).mean()
    m200 = c.rolling(int(p["length200"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    o1, c1 = o.shift(1), c.shift(1)
    bull_e = (c1 < o1) & (c > o) & (c > o1) & (o < c1)
    bear_e = (c1 > o1) & (c < o) & (c < o1) & (o > c1)
    buy = ((m21 > m200) & (m21.shift(1) <= m200.shift(1)) & (c > m21) & (c > m50) & (r < 70) & bull_e).to_numpy()
    sell = ((m21 < m200) & (m21.shift(1) >= m200.shift(1)) & (c < m21) & (c < m50) & (r > 30) & bear_e).to_numpy()
    sl, tp = float(p["sl_pct"]), float(p["tp_pct"])
    ov = o.to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se, sx = (np.zeros(m, dtype=bool) for _ in range(3))
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and (lv[i] <= ov[entry_i] * (1 - sl) or hv[i] >= ov[entry_i] * (1 + tp)):
            pos = 0
        if i + 1 >= m:
            continue
        if buy[i] and pos != 1:
            le[i], pos, entry_i = True, 1, i + 1
        elif sell[i] and pos != -1:
            se[i], pos, entry_i = True, -1, i + 1
        elif pos == -1 and i == entry_i:
            sx[i], pos = True, 0          # the wrong-side short levels fill at the next open
    return le, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sx = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _run(bars_df, p)
    ix = bars_df.index
    on = pd.Series(le, index=ix)
    return {"sl_stop": pd.Series(float(p["sl_pct"]), index=ix).where(on).shift(1),
            "tp_stop": pd.Series(float(p["tp_pct"]), index=ix).where(on).shift(1)}


def portfolio_kwargs(**params):
    return {}
