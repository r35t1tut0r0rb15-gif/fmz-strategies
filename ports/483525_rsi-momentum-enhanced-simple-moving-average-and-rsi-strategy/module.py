"""SMA 8 / 21 crosses with RSI 14 not at an extreme and a 1 % stop / 2 % target from the entry price, 6-minute
bars: SMA 8 crossing above SMA 21 with RSI below 70 goes long; SMA 8 crossing below SMA 21 with RSI above 30 goes
short.
Port of FMZ strategy #483525 "基于动量增强型简单移动平均线和RSI的趋势跟踪策略-Momentum-Enhanced-Simple-Moving-Average-and-RSI-Strategy-for-Trend-Following" (WEN - SMA with RSI Strategy).

FMZ source id: 483525

Source
    https://www.fmz.com/strategy/483525 (PineScript v6, FMZ last modified 2025-02-24 10:19:03).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 103-152), SMA 8 / 21, RSI 14, 70 / 30, SL 1 %, TP 2 %
    long = crossover(sma8, sma21) and rsi < 70; short = crossunder(sma8, sma21) and rsi > 30
    exit(stop = avg_price x (1 -+ 1 %), limit = avg_price x (1 +- 2 %)), issued on every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-issued every bar from strategy.position_avg_price, the entry fill: a fixed 1 % / 2 % bracket
      from the fill (house rule), no moving level. (As written the bracket is na on the signal bar, so Pine first
      arms it at the fill bar's close; the house bracket is live from the fill.)
    * The short signal closes the long and enters short; the long entry reverses a short: REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (D4). FREQ = "6min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a fixed bracket from the fill.
    2 generic: PASS, moving averages, RSI and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_483525_sma8_21_cross_rsi_pct_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "6min"  # backtest header period: 6m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 1.5],
    "tp_pct": [2.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 21, "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30, "sl_pct": 1.0, "tp_pct": 2.0}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (rsi < p["rsi_ob"])).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (rsi > p["rsi_os"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
