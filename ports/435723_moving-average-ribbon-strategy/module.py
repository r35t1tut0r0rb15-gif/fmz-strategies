"""Ten-average ribbon, no bar size of its own: three bars in a row with at least eight of ten averages under the close (and a floor test
against the 200 average) go long; the mirror goes short; a long is closed when six of the ten averages are over the close for three
bars in a row (the short mirrors). The default average is the triangular one.
Port of FMZ strategy #435723 "Moving Average Ribbon Strategy" (Moving Average Ribbon).

FMZ source id: 435723

Source
    https://www.fmz.com/strategy/435723 (PineScript v4, FMZ last modified 2023-12-18 12:29:19).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 150-308), averages of 5, 8, 13, 20, 30, 45, 70, 105, 150 and 200 bars; type trima; 3 bars confirmation, 8 of 10 to enter, 6 of 10 to exit
    aboveMost(x, len) = number of averages under close[len] >= x;  aboveConfirmed(3, ma200): for i = 1..3 not (close[i] < ma200[i] and not (ma05[i] > ma105[i] 1.015))
    long: aboveConfirmed(3, ma200) and aboveMost(8, 1..3);  short: belowConfirmed(3, ma200) and belowMost(8, 1..3);  closeLong = belowMost(6, 1..3);  closeShort = aboveMost(6, 1..3)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "confirmed" tests reduce to: no bar of the last three had its close under the 200 average
      while the 5 average was not over 1.015 x the 105 average (and the mirror). The test runs on the three
      bars before the current one (close[1..3]), as written. The default average type is the
      triangular one (SMA of an SMA); the type is in the grid with the EMA. The orders are filled in the
      script's call order at the next open (short entry, long entry, close long, close short). No
      backtest header names a bar size: FREQ = "bar_size_pending" (rule 1); precompute builds the
      bars with the house bar_sizes.build_bars(raw_1m_df, params["bar_size"]); the driver supplies bar_size.
      REVERSAL INTENDED.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average ribbon counts.
    3 crypto-exchange-only: no.
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_435723_ma_ribbon_counts"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "matype": ["trima", "ema"],
    "most": [8, 7],
}
DEFAULT_PARAMS = {"matype": "trima", "most": 8, "exit_most": 6}
LENGTHS = (5, 8, 13, 20, 30, 45, 70, 105, 150, 200)


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def _ma(src, n, kind):
    if kind == "ema":
        return src.ewm(span=n, adjust=False).mean()
    return src.rolling(n).mean().rolling(n).mean()          # trima


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mas = {n: _ma(c, n, p["matype"]) for n in LENGTHS}
    under = sum((c > mas[n]).astype(int) for n in LENGTHS)    # averages under the close
    over = sum((c < mas[n]).astype(int) for n in LENGTHS)     # averages over the close
    ma200, ma105, ma05 = mas[200], mas[105], mas[5]
    most, ex = int(p["most"]), int(p["exit_most"])

    def conf_above(k):
        bad = (c.shift(k) < ma200.shift(k)) & ~(ma05.shift(k) > ma105.shift(k) * 1.015)
        return ~bad.fillna(False)

    def conf_below(k):
        bad = (c.shift(k) > ma200.shift(k)) & ~(ma05.shift(k) < ma105.shift(k) * 0.985)
        return ~bad.fillna(False)

    ab = conf_above(1) & conf_above(2) & conf_above(3)
    bl = conf_below(1) & conf_below(2) & conf_below(3)
    above_most = lambda k: (under.shift(k) >= most)             # noqa: E731
    below_most = lambda k: (over.shift(k) >= most)              # noqa: E731
    long_c = (ab & above_most(1) & above_most(2) & above_most(3)).to_numpy()
    short_c = (bl & below_most(1) & below_most(2) & below_most(3)).to_numpy()
    close_long = ((over.shift(1) >= ex) & (over.shift(2) >= ex) & (over.shift(3) >= ex)).to_numpy()
    close_short = ((under.shift(1) >= ex) & (under.shift(2) >= ex) & (under.shift(3) >= ex)).to_numpy()
    m = len(long_c)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:          # fills at this bar's open, in the script's call order
            e_s, e_l, c_l, c_s = pend
            if e_s and pos >= 0:
                pos = -1
            if e_l and pos <= 0:
                pos = 1
            if c_l and pos == 1:
                pos = 0
            if c_s and pos == -1:
                pos = 0
        held[i] = pos
        pend = (bool(short_c[i]), bool(long_c[i]), bool(close_long[i]), bool(close_short[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
