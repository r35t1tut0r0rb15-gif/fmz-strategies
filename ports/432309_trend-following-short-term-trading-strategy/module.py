"""Noro's SILA vote, 1-hour bars: eight trend votes (WOW channel, best MA, bar colours, a 7 x ATR 3 band trend, DI, the
trend trader stop, RSI 13 and WaveTrend) are added up; the sum reaching +5 turns the state long, -5 turns it short, and
each turn enters that side; always in once started.
Port of FMZ strategy #432309 "Trend Following Short term Trading Strategy" (Noro's SILA v1.6L Strategy).

FMZ source id: 432309

Source
    https://www.fmz.com/strategy/432309 (PineScript v2, FMZ last modified 2023-11-16 11:11:32).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 232-383), sensitivity 5 / 5, all eight votes on, "money" on
    trends = WOW + BestMA + BarColor + SuperTrend(7 x atr 3) + DI(14) + TTS(21, 3 x wma(tr, 21)) + RSI(13) + WTO(10, 21)
    posi = trends >= 5 ? 1 : trends <= -5 ? -1 : posi[1]
    posi turns 1 -> entry long;  posi turns -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each vote is coded as in the source, including the states each keeps until it changes (WOW,
      BestMA, BarColor, the band trend, TTS); DI is +1 / -1 every bar; the RSI vote is +1 when
      (rsi - 50) x 1.5 > -10, else -1 (its second test is always true there); WaveTrend is the sign of
      its signal line. ATR is Wilder; highest(21) / lowest(21) default to high / low; the DI sums use
      Wilder's running form with nz.
    * "Need money?" is on, so the votes are added as they are. The line, background, arrow and
      locomotive inputs only draw. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, dimensionless votes (the band and stop distances are ATR multiples).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_432309_noro_sila_vote"
FAMILY = "multi_indicator_vote"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sens": [5, 3],
    "wow_len": [30, 15],
}
DEFAULT_PARAMS = {"sens": 5, "wow_len": 30}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _hold(up, dn):
    """1 where up, -1 where dn (up first), else the previous state (0 at the start)."""
    out = np.zeros(len(up), dtype=float)
    s = 0.0
    for i in range(len(up)):
        if up[i]:
            s = 1.0
        elif dn[i]:
            s = -1.0
        out[i] = s
    return out


def _tr(h, lo, c):
    c1 = c.shift(1)
    return pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: float(np.dot(a, w) / w.sum()), raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    m = len(c)
    n = int(p["wow_len"])
    # WOW
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    body = (o + c) / 2
    t1 = _hold((body > center).to_numpy(), (body < center).to_numpy())
    t2 = _hold((center > center.shift(1)).to_numpy(), (center < center.shift(1)).to_numpy())
    wow = _hold((t1 == 1) & (t2 == 1), (t1 == -1) & (t2 == -1))
    # BestMA
    so, sc = o.rolling(30).mean(), c.rolling(30).mean()
    bma = _hold((sc > so).to_numpy(), (sc < so).to_numpy())
    # BarColor
    score = (c > o).astype(float).rolling(8).sum()
    bar = _hold((score > 5).to_numpy(), (score < 3).to_numpy())
    # band trend (7 x ATR 3)
    atr3 = _tr(h, lo, c).ewm(alpha=1 / 3, adjust=False).mean()
    upb = ((h + lo) / 2 - 7 * atr3).to_numpy()
    dnb = ((h + lo) / 2 + 7 * atr3).to_numpy()
    cv = c.to_numpy(dtype=float)
    tu, td = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        tu[i] = max(upb[i], tu[i - 1]) if i >= 1 and cv[i - 1] > tu[i - 1] else upb[i]
        td[i] = min(dnb[i], td[i - 1]) if i >= 1 and cv[i - 1] < td[i - 1] else dnb[i]
    tu1, td1 = np.concatenate(([np.nan], tu[:-1])), np.concatenate(([np.nan], td[:-1]))
    sup = _hold(cv > td1, cv < tu1)
    # DI (Wilder running sums with nz)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    str_ = sdp = sdm = 0.0
    di = np.zeros(m)
    for i in range(m):
        ph = hv[i - 1] if i >= 1 else 0.0
        pl = lv[i - 1] if i >= 1 else 0.0
        pc = cv[i - 1] if i >= 1 else 0.0
        trv = max(hv[i] - lv[i], abs(hv[i] - pc), abs(lv[i] - pc))
        up_, dn_ = hv[i] - ph, pl - lv[i]
        dmp = max(up_, 0.0) if up_ > dn_ else 0.0
        dmm = max(dn_, 0.0) if dn_ > up_ else 0.0
        str_ = str_ - str_ / 14 + trv
        sdp = sdp - sdp / 14 + dmp
        sdm = sdm - sdm / 14 + dmm
        di[i] = 1.0 if str_ > 0 and sdp > sdm else -1.0     # DI+ > DI- (same denominator)
    # TTS
    avg_tr = _wma(_tr(h, lo, c), 21)
    hi_l = (h.rolling(21).max().shift(1) - avg_tr.shift(1) * 3).to_numpy()
    lo_l = (lo.rolling(21).min().shift(1) + avg_tr.shift(1) * 3).to_numpy()
    ret, pos_t = 0.0, 0.0
    tts = np.zeros(m)
    for i in range(m):
        if cv[i] > hi_l[i] and cv[i] > lo_l[i]:
            ret = hi_l[i]
        elif cv[i] < lo_l[i] and cv[i] < hi_l[i]:
            ret = lo_l[i]
        if cv[i] > ret:
            pos_t = 1.0
        elif cv[i] < ret:
            pos_t = -1.0
        tts[i] = pos_t
    # RSI 13
    d = c.diff()
    ru = d.clip(lower=0).ewm(alpha=1 / 13, adjust=False).mean()
    rd = (-d.clip(upper=0)).ewm(alpha=1 / 13, adjust=False).mean()
    rsi_main = ((100 - 100 / (1 + ru / rd)) - 50) * 1.5
    rsi_v = np.where((rsi_main > -10).to_numpy(), 1.0, -1.0)
    # WaveTrend
    hlc3 = (h + lo + c) / 3
    esa = hlc3.ewm(span=10, adjust=False).mean()
    dd = (hlc3 - esa).abs().ewm(span=10, adjust=False).mean()
    tci = ((hlc3 - esa) / (0.015 * dd)).ewm(span=21, adjust=False).mean()
    wto = np.sign(tci.fillna(0.0).to_numpy())
    trends = wow + bma + bar + sup + di + tts + rsi_v + wto
    s = float(p["sens"])
    posi = _hold(trends >= s, trends <= -s)
    prev = np.concatenate(([0.0], posi[:-1]))
    le = (posi == 1) & (prev < 1)
    se = (posi == -1) & (prev > -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
