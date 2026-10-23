"""1-minute bars: the close crossing under the cumulative VWAP minus 2 standard deviations (20 bars) of the close goes long, crossing over the VWAP plus 2 deviations goes short; a long closes on a close above the VWAP, a short on a close below; reversing.
Port of FMZ strategy #474675 "VWAP标准差回归均值交易策略-VWAP-Standard-Deviation-Mean-Reversion-Trading-Strategy" (ETHUSD VWAP Fade Strategy).

FMZ source id: 474675

Source
    https://www.fmz.com/strategy/474675 (PineScript v5, FMZ last modified 2024-12-11 15:06:33).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 127-164), VWAP = cum(close x volume) / cum(volume) from the first bar; stdev 20 x 2
    go_long = crossunder(close, vwap - 2 x stdev(close, 20)) -> entry Long;  go_short = crossover(close, vwap + 2 x stdev) -> entry Short
    position_size > 0 and close > vwap -> close Long;  position_size < 0 and close < vwap -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The VWAP never resets: it is cumulative from the first bar of the data, so its value depends on
      where the data starts (weird case, as #437032). The closes act only on a position the bar's
      entries leave unchanged, from the bar after the fill; an opposite entry reverses. Pine's stdev is
      the population deviation. The title names ETHUSD; the rules are generic. REVERSAL INTENDED. No
      sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fades of deviation bands around a cumulative VWAP.
    3 crypto-exchange-only: no (exchange pair in the header only (ETHUSD named in the title)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data) as the cumulative VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474675_cumulative_vwap_2sd_fade_vwap_exit_1m_reversal"
FAMILY = "vwap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "std_mult": [2.0, 3.0],
    "length": [20, 60],
}
DEFAULT_PARAMS = {"std_mult": 2.0, "length": 20}


def precompute(raw_1m_df, symbol_key, **params):
    bars = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    vw = (c * v).cumsum() / v.cumsum()
    sd = c.rolling(int(p["length"])).std(ddof=0) * float(p["std_mult"])
    up, dn = vw + sd, vw - sd
    buy = ((c < dn) & (c.shift(1) >= dn.shift(1))).to_numpy()
    sell = ((c > up) & (c.shift(1) <= up.shift(1))).to_numpy()
    ex_l, ex_s = (c > vw).to_numpy(), (c < vw).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and ex_l[i]:
                new = 0
            elif pos == -1 and ex_s[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
