"""Triple low-lag EMA scalper, 15-minute bars: during 03:00-16:00 UTC (the London and New York windows
together), the fast DEMA 25 crossing above both DEMA 50 and DEMA 100 on one bar goes long, crossing
below both goes short; each trade has a small take-profit and a stop.
Port of FMZ strategy #428000 "Triple EMA Momentum Strategy" (Triple EMA Scalper low lag, capam).

FMZ source id: 428000

Source
    https://www.fmz.com/strategy/428000 (PineScript v4, FMZ last modified 2023-09-27 17:19:26).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 187-252), EMAs 25 / 50 / 100 (as 2 ema - ema(ema)), TP 50 / SL 100 ticks
    long = crossover(fast, standard) and crossover(fast, slow) during 0300-1100 or 0800-1600 -> entry long
    short mirrors -> entry short; exit(profit = 50, loss = 100) ticks

Interpretation choices (Pine rules in SURVEY_README.md)
    * The sessions are read in the source exchange's time (Binance: UTC); both switches are on, so
      the window is 03:00-16:00 UTC by bar open time.
    * Criterion 2: the tick distances become tp_atr / sl_atr x Wilder ATR(14) of the signal bar (as
      fractions of its close, shifted one bar inside stops(), re-based on the fill). 5 / 10 USD on
      15-minute BTC with a 0.1 tick is about 0.1 / 0.2 ATR (judgement before any backtest).
    * The risk-based lot size is sizing. Stop module: portfolio_kwargs {} (driver D4);
      REVERSAL INTENDED. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based size stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: trading window 03:00-16:00 UTC (the source's London 0300-1100 and New York 0800-1600 in exchange time, UTC on Binance), by bar open time.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428000_triple_dema_session_scalper"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [0.1, 1.0],
    "sl_atr": [0.2, 2.0],
    "len1": [25, 15],
}
DEFAULT_PARAMS = {"len1": 25, "len2": 50, "len3": 100, "tp_atr": 0.1, "sl_atr": 0.2, "atr_length": 14,
                  "win_start": 3, "win_end": 16}


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


def _dema(c, n):
    e = c.ewm(span=n, adjust=False).mean()
    return 2 * e - e.ewm(span=n, adjust=False).mean()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s, sl = _dema(c, int(p["len1"])), _dema(c, int(p["len2"])), _dema(c, int(p["len3"]))
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))
    xu = lambda a, b: (a < b) & (a.shift(1) >= b.shift(1))
    utc = bars_df.index.tz_convert("UTC")
    in_win = pd.Series((utc.hour >= int(p["win_start"])) & (utc.hour < int(p["win_end"])), index=bars_df.index)
    long_e = (xo(f, s) & xo(f, sl) & in_win).astype(bool)
    short_e = (xu(f, s) & xu(f, sl) & in_win).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    pc = bars_df["close"].shift(1)
    tr = pd.concat([bars_df["high"] - bars_df["low"], (bars_df["high"] - pc).abs(),
                    (bars_df["low"] - pc).abs()], axis=1).max(axis=1, skipna=False)
    frac = _rma(tr, int(p["atr_length"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
