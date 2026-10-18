"""Fast RSI scalper, 15-minute bars: counter-trend buys on a red candle with the RSI 7 under 30 (while flat or under the entry price), on a new lower body after a red candle, and after two red bars; the
mirror sells; a long closes (and a short too) when an opposite-colour candle with a large body arrives while the RSI is back past its limit. Martingale and SMA filter are off.
Port of FMZ strategy #436252 "Noro的快速RSI切换策略v17Fast-Scalping-RSI-Switching-Strategy-v17" (Noro's Fast RSI Strategy v1.7).

FMZ source id: 436252

Source
    https://www.fmz.com/strategy/436252 (PineScript v2, FMZ last modified 2023-12-22 15:10:40).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 214-311), RSI 7 at 30 / 70; body filters average / 5 and / 2; Fast RSI, Min/Max and BarColor strategies on
    up1 = red candle and (flat or close < avg price) and rsi7 < 30 and body > avgbody / 5;  dn1 = green candle and (flat or close > avg price) and rsi7 > 70 and body > avgbody / 5;  up2 = a lower red body after a red bar and rsi < 70;  dn2 mirror;  up3 = two red bars;  dn3 = two green bars
    exit = (long and rsi > 30 and green candle) or (short and rsi < 70 and red candle), with body > avgbody / 2
    up: close shorts, entry long;  dn: close longs, entry short;  exit: close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions that read the position (flat, close under the average price) use the position at the
      bar's open: the average price is the entry fill (the next open). The orders of one bar are filled in the
      script's call order at the next open (close of a short, entry long, close of a long, entry short,
      close_all). The martingale lot and the date range are sizing / the author's window. REVERSAL
      INTENDED. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, position-dependent entry conditions followed inside simulate.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital percent and the martingale switch stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426461 (3 members, best partner #426461, Jaccard 0.761); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436252_noro_fast_rsi_scalper"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [7, 5],
    "limit": [30, 25],
}
DEFAULT_PARAMS = {"fast": 7, "limit": 30}


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
    n = int(p["fast"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = pd.Series(np.where(dn_ == 0, 100.0, np.where(up_ == 0, 0.0, 100 - 100 / (1 + up_ / dn_))), index=c.index)
    bar = pd.Series(np.where(c > o, 1, np.where(c < o, -1, 0)), index=c.index)
    limit = float(p["limit"])
    uplimit, dnlimit = 100 - limit, limit
    body = (c - o).abs()
    abody = body.rolling(10).mean()
    mn, mx = np.minimum(c, o), np.maximum(c, o)
    mins = ((mn < mn.shift(1)) & (bar == -1) & (bar.shift(1) == -1)).fillna(False).to_numpy()
    maxs = ((mx > mx.shift(1)) & (bar == 1) & (bar.shift(1) == 1)).fillna(False).to_numpy()
    up2 = mins & (rsi < 70).fillna(False).to_numpy()
    dn2 = maxs & (rsi > 30).fillna(False).to_numpy()
    up3 = ((bar + bar.shift(1)) / 2 == -1).fillna(False).to_numpy()
    dn3 = ((bar + bar.shift(1)) / 2 == 1).fillna(False).to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    rv, bv, bd, ab = rsi.to_numpy(), bar.to_numpy(), body.to_numpy(), abody.to_numpy()
    m = len(cv)
    held = np.zeros(m, dtype=np.int8)
    pos, avg = 0, np.nan
    ops = []
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the script's call order
            for op in ops:
                if op == "eL" and pos <= 0:
                    pos, avg = 1, ov[i]
                elif op == "eS" and pos >= 0:
                    pos, avg = -1, ov[i]
                elif op == "X" and pos != 0:
                    pos, avg = 0, np.nan
                elif op == "XS" and pos < 0:
                    pos, avg = 0, np.nan
                elif op == "XL" and pos > 0:
                    pos, avg = 0, np.nan
        held[i] = pos
        ops = []
        big5 = bd[i] > ab[i] / 5
        up1 = bv[i] == -1 and (pos == 0 or cv[i] < avg) and rv[i] < dnlimit and big5
        dn1 = bv[i] == 1 and (pos == 0 or cv[i] > avg) and rv[i] > uplimit and big5
        up = up1 or up2[i] or up3[i]
        dn = dn1 or dn2[i] or dn3[i]
        exit_ = ((pos > 0 and rv[i] > dnlimit and bv[i] == 1) or (pos < 0 and rv[i] < uplimit and bv[i] == -1)) \
            and bd[i] > ab[i] / 2
        if up:
            if pos < 0:
                ops.append("XS")
            ops.append("eL")
        if dn:
            if pos > 0:
                ops.append("XL")
            ops.append("eS")
        if exit_:
            ops.append("X")
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
