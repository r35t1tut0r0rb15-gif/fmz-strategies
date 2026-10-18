"""Double band breakout, 15-minute bars: a close over the inner upper band (average + 0.25 sd of the average) while the outer upper band rises goes long; a close under the inner lower band while the outer lower
band falls goes short; each side exits when price falls back through its outer band or crosses the 100-bar average.
Port of FMZ strategy #436499 "Double Bollinger Bands Breakout Strategy" (BB Strat).

FMZ source id: 436499

Source
    https://www.fmz.com/strategy/436499 (PineScript v2, FMZ last modified 2023-12-25 13:20:31).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 138-177), length 100, inner 0.25, outer 1.5; take-profit, stop-loss and trailing inputs off
    ma = sma(close, 100);  sd = stdev(ma, 100);  inu = ma + 0.25 sd, outu = ma + 1.5 sd (lower mirror);  longCondition = close > inu and rising(outu, 1);  exitlong = (open[1] > outu and close < outu) or crossunder(close, ma)
    shortCondition = close < inb and falling(outb, 1);  exitshort = (open[1] < outb and close > outb) or crossover(close, ma);  entry Long / close Long / entry Short / close Short in that order

Interpretation choices (Pine rules in SURVEY_README.md)
    * The deviation is that of the AVERAGE series (not of the close), population form. The four rules
      of one bar are filled at the next open in the script's call order (entry Long, close Long, entry
      Short, close Short); a close only acts on a position of its own side. The optional take profit /
      stop / trailing exit inputs default to 0 (off) and are not ported. REVERSAL INTENDED. The
      percent-of-equity size is sizing. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: REVIEW, optional bracket inputs default to off.
    2 generic: PASS, band breakout.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the optional bracket inputs stored.
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

NAME = "fmz_436499_double_bollinger_breakout"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "l": [100, 50],
    "pbin": [0.25, 0.5],
}
DEFAULT_PARAMS = {"l": 100, "pbin": 0.25, "pbout": 1.5}


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
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["l"])
    ma = c.rolling(n).mean()
    sd = ma.rolling(n).std(ddof=0)
    inu, inb = ma + sd * float(p["pbin"]), ma - sd * float(p["pbin"])
    outu, outb = ma + sd * float(p["pbout"]), ma - sd * float(p["pbout"])
    long_c = ((c > inu) & (outu > outu.shift(1))).fillna(False).to_numpy()
    short_c = ((c < inb) & (outb < outb.shift(1))).fillna(False).to_numpy()
    xdn = (c < ma) & (c.shift(1) >= ma.shift(1))
    xup = (c > ma) & (c.shift(1) <= ma.shift(1))
    exl = (((o.shift(1) > outu) & (c < outu)) | xdn).fillna(False).to_numpy()
    exs = (((o.shift(1) < outb) & (c > outb)) | xup).fillna(False).to_numpy()
    m = len(c)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    ops = []
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the script's call order
            for op in ops:
                if op == "eL" and pos <= 0:
                    pos = 1
                elif op == "eS" and pos >= 0:
                    pos = -1
                elif op == "XL" and pos > 0:
                    pos = 0
                elif op == "XS" and pos < 0:
                    pos = 0
        held[i] = pos
        ops = []
        if long_c[i]:
            ops.append("eL")
        if exl[i]:
            ops.append("XL")
        if short_c[i]:
            ops.append("eS")
        if exs[i]:
            ops.append("XS")
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
