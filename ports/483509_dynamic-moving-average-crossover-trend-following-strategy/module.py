"""EMA 13 / 21 crossings on the SMA 120 side or SMA 120 crossings after 5 bars clear of it, 1-minute bars, from flat: long or short with a stop at the larger of 0.2 % and the distance to EMA 13 and a target 5 times it, all from the signal close; once the trade is 0.8 % in profit (bar high / low) it is closed at the next open; the opposite EMA cross closes.
Port of FMZ strategy #483509 "Dynamic Moving Average Crossover Trend Following Strategy" (交易策略（自定义EMA/SMA参数）).

FMZ source id: 483509

Source
    https://www.fmz.com/strategy/483509 (PineScript v5, FMZ last modified 2025-02-24 09:46:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-181), SMA 120; EMA 13 / 21; stop max(0.2 %, distance to EMA 13); target 5 x stop; trail after 0.8 % (0.3 % behind the extreme); 10 % of equity, capital 100000
    long = (close > sma and crossover(ema13, ema21)) or (crossover(close, sma) and low[1..5] > sma[1..5]);  short mirror;  entries only when flat
    entry -> exit(stop = close x (1 - s), limit = close x (1 + 5 s)), s = max(0.002, (close - ema13) / close)
    long and high >= entry x 1.008 -> exit(stop = highest x 0.997, limit = entry x (1 + 5 x (entry - stop) / entry));  long and crossunder(ema13, ema21) -> close Long;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the trailing step makes the new target BELOW the entry for a long (its stop is already
      above the entry, so (entry - stop) / entry is negative): that limit is marketable, so the trade
      closes at the next open once the bar's high reaches entry x 1.008 (mirror for shorts). The port
      sends that as an exit signal. Before it, the opening bracket is fixed at the signal close and sent
      as fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). The flat gate is followed in the signal loop with the bracket checked on each bar's high /
      low (as 449508). Entries only from flat: Opposite entries cannot occur. Stop module:
      portfolio_kwargs {} (driver D4). The 10 % of equity size and the capital are sizing. FREQ = "1min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket as fractions of the fill, profit trigger as an exit signal.
    2 generic: PASS, EMA / SMA crossings with an EMA-distance bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483509_ema13_21_sma120_cross_ema_dist_bracket_profit_trigger_flat"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sma_length": [120, 60],
    "ema_fast_period": [13, 9],
}
DEFAULT_PARAMS = {"sma_length": 120, "ema_fast_period": 13, "ema_slow_period": 21, "stop_floor": 0.002,
                  "tp_mult": 5.0, "trigger": 0.008}


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


def _plan(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    sma = c.rolling(int(p["sma_length"])).mean()
    ef = c.ewm(span=int(p["ema_fast_period"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow_period"]), adjust=False).mean()
    xu = (ef > es) & (ef.shift(1) <= es.shift(1))
    xd = (ef < es) & (ef.shift(1) >= es.shift(1))
    cu = (c > sma) & (c.shift(1) <= sma.shift(1))
    cd = (c < sma) & (c.shift(1) >= sma.shift(1))
    clear_up = pd.Series(True, index=c.index)
    clear_dn = pd.Series(True, index=c.index)
    for k in range(1, 6):
        clear_up = clear_up & (lo.shift(k) > sma.shift(k))
        clear_dn = clear_dn & (h.shift(k) < sma.shift(k))
    lc = (((c > sma) & xu) | (cu & clear_up)).to_numpy()
    sc = (((c < sma) & xd) | (cd & clear_dn)).to_numpy()
    xuv, xdv = xu.to_numpy(), xd.to_numpy()
    ov, hv, lv, cv, efv = (x.to_numpy(dtype=float) for x in (o, h, lo, c, ef))
    fl, tm, trg = float(p["stop_floor"]), float(p["tp_mult"]), float(p["trigger"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    sl_lv, tp_lv = np.full(m, np.nan), np.full(m, np.nan)
    pos, pend, out_pend = 0, 0, False
    sl = tp = ep = np.nan
    for i in range(m):
        if out_pend:
            pos, out_pend = 0, False
        if pend != 0:
            pos, pend = pend, 0
            sl, tp, ep = sl_lv[i - 1], tp_lv[i - 1], cv[i - 1]
            if (pos > 0 and (sl >= ov[i] or tp <= ov[i])) or (pos < 0 and (sl <= ov[i] or tp >= ov[i])):
                if pos > 0:
                    lx[i] = True
                else:
                    sx[i] = True
                out_pend = True               # marketable at the fill: closed one bar late
        if pos != 0 and not out_pend:
            if (pos > 0 and (lv[i] <= sl or hv[i] >= tp)) or (pos < 0 and (hv[i] >= sl or lv[i] <= tp)):
                pos = 0                       # the bracket closes it inside the bar
        if pos == 0 and not out_pend and pend == 0:
            if lc[i]:
                s = max(fl, (cv[i] - efv[i]) / cv[i])
                le[i], pend = True, 1
                sl_lv[i], tp_lv[i] = cv[i] * (1 - s), cv[i] * (1 + tm * s)
            elif sc[i]:
                s = max(fl, (efv[i] - cv[i]) / cv[i])
                se[i], pend = True, -1
                sl_lv[i], tp_lv[i] = cv[i] * (1 + s), cv[i] * (1 - tm * s)
        if pos > 0 and not out_pend and (hv[i] >= ep * (1 + trg) or xdv[i]):
            lx[i], out_pend = True, True
        if pos < 0 and not out_pend and (lv[i] <= ep * (1 - trg) or xuv[i]):
            sx[i], out_pend = True, True
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx), S(se), S(sx), S(sl_lv), S(tp_lv)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _, _ = _plan(bars_df, p)
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _, sl_lv, tp_lv = _plan(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - sl_lv.shift(1) / o, tp_lv.shift(1) / o - 1
    s_sl, s_tp = sl_lv.shift(1) / o - 1, 1 - tp_lv.shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
