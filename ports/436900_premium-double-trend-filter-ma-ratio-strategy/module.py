"""Percentile of the SMA 10 / 50 ratio with Bollinger-width and SMA trend filters and a tick bracket, 3-minute bars: the ratio's 50-bar percentile rank crossing over 10 with a narrow band (width percentile under 30)
above the SMA 50 and SMA 200 goes long, crossing under 90 with the mirror filters goes short, reversing; brackets re-expressed as ATR multiples.
Port of FMZ strategy #436900 "Premium Double Trend Filter MA Ratio Strategy" (Premium MA Ratio Strategy).

FMZ source id: 436900

Source
    https://www.fmz.com/strategy/436900 (PineScript v4, FMZ last modified 2023-12-28 17:37:14).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 124-255), MA 10 / 50, thresholds 10 / 90, BB 20 x 2 with width percentile < 30, trend SMA 50 / 200, TP 150 / SL 100 ticks, combined exit 50 / 50 ticks (longs), time filter off
    premium = sma 10 / sma 50 x 100;  pct = share of the last 50 values below the current (percentile_rank);  bb_pct = the same rank of the 20-bar Bollinger width
    long = crossover(pct, 10) and bb_pct < 30 and close > sma 50 and close > sma 200;  short = crossunder(pct, 90) and the mirrors;  exits: TP 150, SL 100 (both sides), combined loss / profit 50 (Buy only), in ticks

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each strategy.exit closes the whole position, so the nearest level of each side wins: a long has a
      50-tick stop and target (the combined exit), a short a 100-tick stop and a 150-tick target.
      Criterion 2: ticks -> ATR multiples, sl_stop = k_atr x ATR(14) / close per 100 ticks (long 0.5 k /
      0.5 k, short 1.0 k / 1.5 k), of the signal bar, shifted one bar inside stops() (re-based on the fill);
      0.25 is the reading (100 ticks of 0.1 on BTC against a 3-minute ATR near 40), 1.0 a wider stop. The
      percentile rank counts strictly lower earlier values over i = 1 .. length. The time filter is off and
      not ported. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ =
      "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; brackets fixed at entry.
    2 generic: ADAPT, tick brackets -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the hour filter is off).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436900_ma_ratio_percentile_bracket"
FAMILY = "trend_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "slow_length": [50, 100],
    "k_atr": [0.25, 1.0],
}
DEFAULT_PARAMS = {"fast_length": 10, "slow_length": 50, "k_atr": 0.25, "buy_th": 10.0, "sell_th": 90.0,
                  "bb_length": 20, "bb_dev": 2.0, "bb_width_th": 30.0, "trend1": 50, "trend2": 200, "atr_len": 14,
                  "long_sl": 0.5, "long_tp": 0.5, "short_sl": 1.0, "short_tp": 1.5}


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


def _pct_rank(x, n):
    """Pine loop: rank = number of i in 1 .. n with x > x[i] (na comparisons false); rank / n x 100."""
    cnt = pd.Series(0.0, index=x.index)
    for i in range(1, n + 1):
        cnt = cnt + (x > x.shift(i)).astype(float)
    return cnt / n * 100.0


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _setup(bars_df, p):
    c = bars_df["close"]
    prem = c.rolling(int(p["fast_length"])).mean() / c.rolling(int(p["slow_length"])).mean() * 100.0
    pr = _pct_rank(prem, int(p["slow_length"]))
    bl = int(p["bb_length"])
    width = 2.0 * float(p["bb_dev"]) * c.rolling(bl).std(ddof=0)
    bw = _pct_rank(width, bl)
    t1, t2 = c.rolling(int(p["trend1"])).mean(), c.rolling(int(p["trend2"])).mean()
    b, s = float(p["buy_th"]), float(p["sell_th"])
    narrow = bw < float(p["bb_width_th"])
    lc = (pr > b) & (pr.shift(1) <= b) & narrow & (c > t1) & (c > t2)
    sc = (pr < s) & (pr.shift(1) >= s) & narrow & (c < t1) & (c < t2)
    f = float(p["k_atr"]) * _atr(bars_df, p["atr_len"]) / c
    sl = pd.Series(np.where(lc, float(p["long_sl"]) * f, np.where(sc, float(p["short_sl"]) * f, np.nan)), index=c.index)
    tp = pd.Series(np.where(lc, float(p["long_tp"]) * f, np.where(sc, float(p["short_tp"]) * f, np.nan)), index=c.index)
    return lc, sc, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lc, sc, _, _ = _setup(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lc, false, sc, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
