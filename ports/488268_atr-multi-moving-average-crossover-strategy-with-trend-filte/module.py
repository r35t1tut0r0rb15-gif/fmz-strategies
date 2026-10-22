"""SMA 20 / EMA 89 crossings on the side of the SMA 200, 2-hour bars, from flat: the up-cross goes long and the down-cross goes short, each with a 2 ATR 14 stop and a 3 ATR target from the signal close.
Port of FMZ strategy #488268 "趋势过滤多均线交叉ATR风控量化策略-Multi-Moving-Average-Crossover-Strategy-with-Trend-Filter-and-ATR-Risk-Management" (EMA Cross Strategy (20MA & 89EMA with 200MA Filter)).

FMZ source id: 488268

Source
    https://www.fmz.com/strategy/488268 (PineScript v5, FMZ last modified 2025-03-26 13:42:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 206-250), SMA 20; EMA 89; SMA 200; ATR 14; SL 2 ATR; TP 3 ATR; capital 10000
    close > sma200 and flat and crossover(sma20, ema89) -> entry Long + exit(stop = close - 2 atr, limit = close + 3 atr)
    close < sma200 and flat and crossunder(sma20, ema89) -> entry Short + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close and ATR and sent as fractions of the fill open
      (a level at or through it is marketable and closed one bar late, as #458256). Entries need a flat
      position at the bar's close, so a loop follows the bracket on each bar's high / low (as #449508).
      Opposite entries cannot occur (entries only from flat). Stop module: portfolio_kwargs {} (driver D4).
      Stops on bars longer than 1 hour: mark coarse_bar_stop. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, MA crossings with a long-SMA filter and an ATR bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: strategy(): capital 10000 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_488268_sma20_ema89_cross_sma200_side_atr_bracket_flat"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stopLossMultiplier": [2.0, 1.5],
    "takeProfitMultiplier": [3.0, 4.5],
}
DEFAULT_PARAMS = {"stopLossMultiplier": 2.0, "takeProfitMultiplier": 3.0, "atr_length": 14}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    m20 = c.rolling(20).mean()
    e89 = c.ewm(span=89, adjust=False).mean()
    m200 = c.rolling(200).mean()
    lc = ((c > m200) & (m20 > e89) & (m20.shift(1) <= e89.shift(1))).to_numpy()
    sc = ((c < m200) & (m20 < e89) & (m20.shift(1) >= e89.shift(1))).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    av = _rma(tr, int(p["atr_length"])).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    ks, kt = float(p["stopLossMultiplier"]), float(p["takeProfitMultiplier"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, sl, tp, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, sl, tp = pend, 0, sl_n, tp_n
            through = (sl >= ov[i] or tp <= ov[i]) if pos == 1 else (sl <= ov[i] or tp >= ov[i])
            if through:                          # a level through the fill: closed at the next open
                if pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                pend = 2
        elif pend == 2:
            pos, pend = 0, 0
        if pos == 1 and pend == 0 and (lv[i] <= sl or hv[i] >= tp):
            pos = 0                              # the bracket fills inside this bar
        elif pos == -1 and pend == 0 and (hv[i] >= sl or lv[i] <= tp):
            pos = 0
        if pos != 0 or pend != 0:
            continue
        if lc[i]:
            sl_n, tp_n = cv[i] - av[i] * ks, cv[i] + av[i] * kt
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i]:
            sl_n, tp_n = cv[i] + av[i] * ks, cv[i] - av[i] * kt
            se[i], pend, sl_sent[i], tp_sent[i], side[i] = True, -1, sl_n, tp_n, -1
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, se, sx, sl_sent, tp_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, tp_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, tp_l, sd = sl_l.shift(1), tp_l.shift(1), sd.shift(1)    # the signal bar's levels, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    tp_f = (tp_l / o - 1).where(sd > 0, 1 - tp_l / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
