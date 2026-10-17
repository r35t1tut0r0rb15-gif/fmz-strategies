"""Rising-ADX turns on the EMA 20 side, 1-hour bars: the ADX 14 above 10 turning up while the ADX of the previous bar's
highs / lows turns down, with the close above the EMA 20, goes long; the same turn with the close below it goes short;
the opposite ADX turn or the close crossing to the other side of the EMA closes the position.
Port of FMZ strategy #435020 "动态上升ADX趋势跟踪策略Dynamic-Rising-ADX-Trend-Following-Strategy" (Rising ADX strategy).

FMZ source id: 435020

Source
    https://www.fmz.com/strategy/435020 (PineScript v4, FMZ last modified 2023-12-11 17:18:32).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 125-179), ADX 14 / DI 14, threshold 10; both averages EMA 20; long and short on
    sig = adx(high, low, tr);  prev_sig = adx(high[1], low[1], tr);  long = sig > 10 and rising(sig, 1) and falling(prev_sig, 1) and close > ema20
    long and position_size < 1 -> entry long;  (rising(prev_sig, 1) and falling(sig, 1)) or close < ema20 -> close long;  shorts mirror (position_size < 1)

Interpretation choices (Pine rules in SURVEY_README.md)
    * prev_sig feeds the previous bar's high / low with the current true range, as written. The
      short entry also needs position_size < 1, so it cannot reverse an open long (the default
      quantity 1), while a long entry reverses a short, as written. The closes act on the position
      held on the bar; an entry on the same bar wins. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ADX turns and an average side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED (long entries reverse shorts; short entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435020_rising_adx_ema_side"
FAMILY = "directional_movement"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "threshold": [10, 20],
    "ma_len": [20, 50],
}
DEFAULT_PARAMS = {"adx_len": 14, "di_len": 14, "threshold": 10, "ma_len": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fixnan(v, index):
    """Pine fixnan: a NaN (or inf) takes the last valid value before it (past values only)."""
    out = np.array(v, dtype=float)
    last = np.nan
    for i in range(len(out)):
        if np.isfinite(out[i]):
            last = out[i]
        else:
            out[i] = last
    return pd.Series(out, index=index)


def _adx(h, lo, tr, di_len, adx_len):
    up, dn = h.diff(), -lo.diff()
    rma = lambda x, n: x.ewm(alpha=1 / n, adjust=False).mean()  # noqa: E731
    trur = rma(tr, di_len)
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=h.index).where(up.notna())
    ndm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=h.index).where(dn.notna())
    plus = _fixnan((100 * rma(pdm, di_len) / trur).to_numpy(), h.index)
    minus = _fixnan((100 * rma(ndm, di_len) / trur).to_numpy(), h.index)
    s = plus + minus
    return 100 * rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    dl, al = int(p["di_len"]), int(p["adx_len"])
    sig = _adx(h, lo, tr, dl, al)
    psig = _adx(h.shift(1), lo.shift(1), tr, dl, al)
    ema = c.ewm(span=int(p["ma_len"]), adjust=False).mean()
    up_s, dn_s = sig > sig.shift(1), sig < sig.shift(1)
    up_p, dn_p = psig > psig.shift(1), psig < psig.shift(1)
    turn = (sig > float(p["threshold"])) & up_s & dn_p
    lc, sc = (turn & (c > ema)).to_numpy(), (turn & (c < ema)).to_numpy()
    xl = ((up_p & dn_s) | (c < ema)).to_numpy()
    xs = ((up_p & dn_s) | (c > ema)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and xl[i]:
            new = 0
        if pos == -1 and xs[i]:
            new = 0
        if lc[i] and pos < 1:
            new = 1
        if sc[i] and pos < 1:
            new = -1
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
