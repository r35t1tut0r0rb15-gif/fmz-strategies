"""Counter-candle entries inside a 09:15-14:55 session with the 14-bar money flow index, the choppiness index under 50 and rising volume, 2-hour bars: a down candle with MFI under 25 goes long, an up candle with MFI over 75 goes short; every position is squared off at the first bar outside the session; reversing.
Port of FMZ strategy #428621 "力道K线突破策略Choppiness-K-line-Breakthrough-Strategy" ([VJ]War Machine PAT Intra).

FMZ source id: 428621

Source
    https://www.fmz.com/strategy/428621 (PineScript v4, FMZ last modified 2023-10-07 15:59:26).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 202-307), session 0915-1455; MFI 14 of hlc3 (25 / 75); choppiness 14 < 50; volume > volume[1]; TP / SL 5 % (sent only with an average price)
    red candle and mf < 25 and ci < 50 and volume > volume[1] and in session -> entry Long, exit(stop = avg x 0.95, limit = avg x 1.05);  green candle and mf > 75 ... -> entry Short (mirror)
    not in session and position open -> close_all (square-off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The session is read in the header exchange's time (UTC, fixed, no DST) by the bar's open time, as
      time(timeframe.period, session) != 0 does (na != 0 is false). The bracket is sent only on a signal
      bar and uses strategy.position_avg_price of that bar, which is na when flat, so a fresh entry gets no
      bracket; only a repeat signal while in a position would set one: not ported (a session-bound trade
      lasts at most three 2-hour bars; weird case). The money flow is the plain ratio form (no zero
      special cases), as written. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; session square-off.
    2 generic: PASS, counter-candle money-flow extremes in a non-choppy market.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the money flow index of hlc3 and volume > volume[1]; exchange volume to be compared later (Austin, 2026-10-23).
Session open: 09:15-14:55 UTC by bar open (the header exchange's time; fixed UTC, no DST); square-off outside it.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428621_session_counter_candle_mfi14_choppiness_volume_squareoff_reversal"
FAMILY = "session_reversal"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "oversold": [25, 20],
    "trend_factor": [50, 40],
}
DEFAULT_PARAMS = {"oversold": 25, "trend_factor": 50, "length": 14, "sess_start": 555, "sess_end": 895}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["length"])
    src = (h + lo + c) / 3
    ch = src.diff()
    upper = (v * src.where(~(ch <= 0), 0.0)).rolling(n).sum()
    lower = (v * src.where(~(ch >= 0), 0.0)).rolling(n).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        mf = 100.0 - 100.0 / (1.0 + upper / lower)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # atr(1): first bar high - low
    ci = 100 * np.log10(tr.rolling(n).sum() / (h.rolling(n).max() - lo.rolling(n).min())) / np.log10(n)
    utc = bars_df.index.tz_convert("UTC")
    mins = pd.Series(utc.hour * 60 + utc.minute, index=c.index)
    in_sess = (mins >= int(p["sess_start"])) & (mins < int(p["sess_end"]))
    vol_up = v > v.shift(1)
    os_, ob_ = float(p["oversold"]), 100.0 - float(p["oversold"])
    tf = float(p["trend_factor"])
    lc = ((c < o) & (mf < os_) & (ci < tf) & vol_up & in_sess).to_numpy()
    sc = ((c > o) & (mf > ob_) & (ci < tf) & vol_up & in_sess).to_numpy()
    out = (~in_sess).to_numpy()
    m = len(lc)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        old = pos
        if lc[i]:
            pos = 1
        if sc[i]:
            pos = -1
        if out[i] and old != 0 and pos == old:
            pos = 0
        if pos == 1 and old != 1:
            le[i] = True
        elif pos == -1 and old != -1:
            se[i] = True
        elif pos == 0 and old == 1:
            lx[i] = True
        elif pos == 0 and old == -1:
            sx[i] = True
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
