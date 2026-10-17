"""SSL channel flips with an ATR bracket, 2-hour bars: the close above the SMA 16 of the highs turns the SSL state up, below
the SMA 16 of the lows down; a flip from down to up goes long, from up to down short; each trade carries a 1.5 ATR stop
and a 1 ATR target set from the signal close (re-based on the fill).
Port of FMZ strategy #432965 "基于ATR和资金管理的SSL通道回测策略SSL-Channel-Backtester-Strategy-With-ATR-and-Money-Management" (SSL Backtester).

FMZ source id: 432965

Source
    https://www.fmz.com/strategy/432965 (PineScript v4, FMZ last modified 2023-11-23 10:26:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 193-233), SSL 16, ATR 14, stop 1.5 ATR, target 1.0 ATR (the code's default), money management on
    ssl = close > sma(high, 16) ? 1 : close < sma(low, 16) ? -1 : ssl[1]
    ssl > 0 and ssl[1] < 0 -> entry long, exit(stop = close - 1.5 atr, limit = close + 1.0 atr);  mirror -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fixed at the signal bar: sl_atr / tp_atr x ATR / close of the signal bar, shifted
      one bar inside stops() and re-based on the fill (the source measures from the signal close).
      ATR is Wilder's (Pine atr()).
    * The SSL state starts at 0, so the first move to 1 or -1 is not a flip. The money-management lot
      (risk share, pip value, the two-digit switch) is sizing only.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "2h" from the backtest header; stops on bars longer than 1 h: mark coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, channel flips and ATR exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based lot stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_432965_ssl_flip_atr_bracket"
FAMILY = "ssl_channel"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.5, 3.0],
    "tp_atr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"ssl_len": 16, "atr_len": 14, "sl_atr": 1.5, "tp_atr": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["ssl_len"])
    sh, sl = h.rolling(n).mean().to_numpy(), lo.rolling(n).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ssl = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cv[i] > sh[i]:
            q = 1
        elif cv[i] < sl[i]:
            q = -1
        ssl[i] = q
    prev = np.concatenate(([0], ssl[:-1]))
    le = pd.Series((ssl > 0) & (prev < 0), index=c.index)
    se = pd.Series((ssl < 0) & (prev > 0), index=c.index)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return le, se, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
