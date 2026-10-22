"""EMA 20 / 50 crossings on the EMA 200 side with RSI 14, Bollinger 20 and MACD filters, 2-hour bars: the cross up above the EMA 200 goes long, the cross down below it goes short; a 2 % / 3 % bracket exists only on a reversal, from the replaced position's price; reversing.
Port of FMZ strategy #481365 "Multi-Indicator-Trend-Following-Strategy-with-Dynamic-Risk-Management-多指标趋势跟踪策略与动态风险管理" (Altcoin Long/Short Strategy).

FMZ source id: 481365

Source
    https://www.fmz.com/strategy/481365 (PineScript v5, FMZ last modified 2025-02-10 15:05:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-159), EMA 20 / 50 / 200; RSI 14; BB 20 / 2; MACD 12 / 26 / 9; stop 2 %, R:R 1.5 of strategy.position_avg_price (long formulas for both sides); 200 % of equity; commission 0.1 %
    close > ema200 and crossover(ema20, ema50) and rsi > 50 and close > lower and macd > signal -> entry Long + exit(stop = avg x 0.98, limit = avg x 1.03);  mirror -> entry Short + exit(same formulas)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on the signal bar from strategy.position_avg_price, which is still the price of
      the position held then: na from flat (no bracket), and the replaced position's fill price on a
      reversal, as written (as #473147); the short uses the long formulas, so its levels are on the wrong
      side and close it one bar after its fill. A loop tracks those prices; the levels are sent as
      fractions of the new fill open (a level at or through it is marketable and closed one bar late).
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour:
      mark coarse_bar_stop. The 200 % of equity size and capital are sizing; the commission is a cost and
      is not ported (house cost model). FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the replaced position's price as the bracket base, as written.
    2 generic: PASS, EMA crossings with trend, momentum and band filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity and capital stored, not ported; commission not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_481365_ema20_50_cross_filters_reversal_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_fast": [20, 10],
    "ema_slow": [50, 100],
}
DEFAULT_PARAMS = {"ema_fast": 20, "ema_slow": 50, "sl_pct": 0.02, "rr": 1.5}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    f = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    e200 = c.ewm(span=200, adjust=False).mean()
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    basis = c.rolling(20).mean()
    dev = 2 * c.rolling(20).std(ddof=0)
    lc = ((c > e200) & (f > s) & (f.shift(1) <= s.shift(1)) & (r > 50) & (c > basis - dev) & (macd > sig)).to_numpy()
    sc = ((c < e200) & (f < s) & (f.shift(1) >= s.shift(1)) & (r < 50) & (c < basis + dev) & (macd < sig)).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    slp = float(p["sl_pct"])
    tpp = slp * float(p["rr"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, avg, sl, tp, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, avg, sl, tp = pend, 0, ov[i], sl_n, tp_n
            through = (sl >= ov[i] or tp <= ov[i]) if pos == 1 else (sl <= ov[i] or tp >= ov[i])
            if through:                          # a level through the fill: closed at the next open
                if pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                pend, sl, tp = 2, np.nan, np.nan
        elif pend == 2:
            pos, pend, avg, sl, tp = 0, 0, np.nan, np.nan, np.nan
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos, avg, sl, tp = 0, np.nan, np.nan, np.nan     # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= sl or lv[i] <= tp):
            pos, avg, sl, tp = 0, np.nan, np.nan, np.nan
        if pend == 2:
            continue
        if lc[i] and pos != 1:
            sl_n, tp_n = avg * (1 - slp), avg * (1 + tpp)    # na from flat
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i] and pos != -1:
            sl_n, tp_n = avg * (1 - slp), avg * (1 + tpp)    # the long formulas, as written
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
