"""Close crossings over the EMA 25 in a stacked EMA 25 / 50 / 100 trend, hourly bars, long only: it buys and closes on a close at or over a 1 R target (R from the 20-bar low) or a close crossing under the EMA 100.
Port of FMZ strategy #475633 "Multi EMA Golden Cross Strategy with Tiered Take Profit" (Golden Cross with Customizable TP/SL).

FMZ source id: 475633

Source
    https://www.fmz.com/strategy/475633 (PineScript v6, FMZ last modified 2024-12-20 16:54:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-151), EMA 25 / 50 / 100 (constants); lookback 20; buffer 0.0003; TP multipliers 1.0 / 1.5; qty 0.5 per id
    ema25 > ema50 > ema100 and crossover(close, ema25) -> entry Buy1 (0.5), entry Buy2 (0.5), sl := lowest(low, 20) - 0.0003, tp1 := close + (close - sl), tp2 := close + 1.5 (close - sl);  close >= tp1 or crossunder(close, ema100) -> close Buy1;  close >= tp2 or crossunder or close <= sl -> close Buy2

Interpretation choices (Pine rules in SURVEY_README.md)
    * With pyramiding 1 only "Buy1" fills ("Buy2" is ignored while Buy1 is held), so the stop and TP2
      tests, which close only Buy2, never act. The levels are stored on every signal bar (also a repeat
      while long) and the closes are bar-close tests, so a loop follows them as written. The 0.0003
      buffer is a price amount, ported as a fraction of 42000 of the close. Long only. The fixed qty is
      not ported. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, trend EMA crossings with a 1 R close target and an EMA 100 exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed qty 0.5 per id stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_475633_ema25_50_100_stack_cross_1r_close_target_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [20, 10],
    "tp_mult1": [1.0, 2.0],
}
DEFAULT_PARAMS = {"lookback": 20, "tp_mult1": 1.0, "buffer_frac": 7.14e-09}


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
    lo, c = bars_df["low"], bars_df["close"]
    e25, e50, e100 = (c.ewm(span=n, adjust=False).mean() for n in (25, 50, 100))
    go = ((e25 > e50) & (e50 > e100) & (c > e25) & (c.shift(1) <= e25.shift(1))).to_numpy()
    xd = ((c < e100) & (c.shift(1) >= e100.shift(1))).to_numpy()
    ll = lo.rolling(int(p["lookback"])).min().to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    k, buf = float(p["tp_mult1"]), float(p["buffer_frac"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, tp1 = 0, 0, np.nan
    for i in range(m):
        pos = nxt
        if go[i]:
            sl = ll[i] - buf * cv[i]
            tp1 = cv[i] + (cv[i] - sl) * k
            if pos == 0:
                le[i], nxt = True, 1
        if pos == 1 and (cv[i] >= tp1 or xd[i]):
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
