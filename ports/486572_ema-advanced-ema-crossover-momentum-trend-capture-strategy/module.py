"""2-hour bars, one side at a time: the close crossing over the EMA 13 on a green bar with ADX 14 over 30 and volume over 1.5 x its 5-bar average goes long (not while short), the mirror goes short (not while long); a long closes at the next open after a bar whose high reaches the signal close + 1.5 ATR 14, a short after its low reaches the signal close - 1.5 ATR; no stop.
Port of FMZ strategy #486572 "高级EMA交叉动量趋势捕捉策略-Advanced-EMA-Crossover-Momentum-Trend-Capture-Strategy" (EMA Scalping - No Stop Loss).

FMZ source id: 486572

Source
    https://www.fmz.com/strategy/486572 (PineScript v6, FMZ last modified 2025-03-14 09:48:47).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 149-215), EMA 13; DMI 14 / 14, ADX > 30; volume SMA 5 x 1.5; ATR 14 x 1.5 target from the signal close
    buyConfirm and strongTrend and volumeSpike and not inShort -> longProfitTarget := close + 1.5 atr, entry Long;  sell mirrored and not inLong -> shortProfitTarget := close - 1.5 atr, entry Short
    inLong and high >= longProfitTarget -> close Long;  inShort and low <= shortProfitTarget -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target test is a high / low check at the bar's close with a market close, so it fills at the
      next open (exact in the signals). A repeated buy signal while long re-sets the target from the new
      close. The position is read at the bar's close, so the test starts on the fill bar. An entry is
      blocked while the opposite side is held, so opposite entries cannot occur. There is no stop, as
      the title says. No sizing code; the commission is a cost. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; high / low-checked target in the signals.
    2 generic: PASS, EMA crossings on strong-trend volume spikes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: commission stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 5; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Opposite entries cannot occur (an entry is blocked while the other side is held).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_486572_ema13_cross_adx_volume_atr_target_no_stop_2h"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [13, 21],
    "tp_atr": [1.5, 2.5],
}
DEFAULT_PARAMS = {"ema_len": 13, "adx_min": 30.0, "tp_atr": 1.5}


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


def _fixnan(x):
    """Pine fixnan: a NaN takes the last non-NaN value (Pine's own indicator semantics)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _dmi(h, lo, c, n, sm):
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trur = _rma(tr, n)
    plus, minus = _fixnan(100 * _rma(pdm, n) / trur), _fixnan(100 * _rma(mdm, n) / trur)
    tot = plus + minus
    adx = 100 * _rma((plus - minus).abs() / tot.where(tot != 0, 1.0), sm)
    return plus, minus, adx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    _, _, adx = _dmi(h, lo, c, 14, 14)
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14).to_numpy()
    ok = (adx > float(p["adx_min"])) & (v > v.rolling(5).mean() * 1.5)
    buy = ((c > e) & (c.shift(1) <= e.shift(1)) & (c > o) & ok).to_numpy()
    sell = ((c < e) & (c.shift(1) >= e.shift(1)) & (c < o) & ok).to_numpy()
    cn, hn, ln = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    k = float(p["tp_atr"])
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, lt, st = 0, np.nan, np.nan
    for i in range(m):
        held = tgt                          # the position at this bar's close (filled at its open)
        new = held
        if buy[i] and held != -1:
            lt = cn[i] + atr[i] * k
            if held == 0:
                new = 1
        if sell[i] and held != 1:
            st = cn[i] - atr[i] * k
            if held == 0:
                new = -1                    # a buy and a sell never meet on one bar
        if held == 1 and hn[i] >= lt:
            new = 0
        elif held == -1 and ln[i] <= st:
            new = 0
        if new != held and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif held == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
