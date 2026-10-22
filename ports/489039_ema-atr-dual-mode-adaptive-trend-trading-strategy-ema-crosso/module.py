"""EMA 3 / 8 crossings, broker days, from flat and at least 72 bars after the last entry: in a trending market (RSI 14 more than 15 from 50) a cross in the EMA 55 and SMA 5 / 20 direction, otherwise a cross against the EMA 55, goes long or short, each with a 1.2 ATR 14 stop and a 2 ATR target from the signal close.
Port of FMZ strategy #489039 "双模式自适应趋势交易策略EMA交叉结合ATR波动率风险管理系统-Dual-Mode-Adaptive-Trend-Trading-Strategy-EMA-Crossover-with-ATR-Volatility-Based-Risk-Management-System" (DOGE/USDT 5X Adaptive Trend Strategy).

FMZ source id: 489039

Source
    https://www.fmz.com/strategy/489039 (PineScript v6, FMZ last modified 2025-04-01 14:20:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 234-322), EMA 3 / 8 / 55; ATR 14; interval 72 bars; SL 1.2 ATR, TP 2 ATR; adaptive (on), RSI 14; risk 1 % x 5 sizing
    trending = |rsi - 50| / 50 > 0.3;  trend entry: crossover(ema3, ema8) and close > ema55 and sma5 > sma20;  counter entry: crossover and close < ema55 and not trending
    flat and bar - last entry bar >= 72 and (trending ? trend entry : counter entry) -> entry Long + exit(stop = close - 1.2 atr, limit = close + 2 atr), last entry bar := bar;  mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "minutes between trades" input is compared with a bar count, so it is 72 bars, as written; the
      counter starts at bar 0 of the data. Entries need a flat position at the bar's close, so a loop
      follows the bracket on each bar's high / low (as #449508); the bracket is set on the signal bar and
      sent as fractions of the fill open (a level at or through it is marketable and closed one bar late,
      as #458256). Opposite entries cannot occur (entries only from flat). Stop module: portfolio_kwargs {}
      (driver D4). Stops on daily bars: mark coarse_bar_stop. The risk-sized leveraged quantity is sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, EMA crossings, trend or counter-trend by RSI distance, with an ATR bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: risk-sized leveraged quantity and margins stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489039_ema3_8_cross_adaptive_trend_counter_atr_bracket_flat"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tradeInterval": [72, 10],
    "slMultiplier": [1.2, 2.0],
}
DEFAULT_PARAMS = {"tradeInterval": 72, "slMultiplier": 1.2, "tpMultiplier": 2.0, "fastEMA": 3, "slowEMA": 8,
                  "trendEMA": 55, "atrPeriod": 14, "adaptivePeriod": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    f, s, t = ema(p["fastEMA"]), ema(p["slowEMA"]), ema(p["trendEMA"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    av = _rma(tr, int(p["atrPeriod"])).to_numpy()
    trending = ((_rsi(c, int(p["adaptivePeriod"])) - 50).abs() / 50 > 0.3)
    up_t = c.rolling(5).mean() > c.rolling(20).mean()
    dn_t = c.rolling(5).mean() < c.rolling(20).mean()
    xu = (f > s) & (f.shift(1) <= s.shift(1))
    xd = (f < s) & (f.shift(1) >= s.shift(1))
    lc = (xu & (((c > t) & up_t & trending) | ((c < t) & ~trending))).to_numpy()
    sc = (xd & (((c < t) & dn_t & trending) | ((c > t) & ~trending))).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    ks, kt = float(p["slMultiplier"]), float(p["tpMultiplier"])
    gap = int(p["tradeInterval"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, sl, tp, sl_n, tp_n, last = 0, 0, np.nan, np.nan, np.nan, np.nan, 0
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
        if pos != 0 or pend != 0 or i - last < gap:
            continue
        if lc[i]:
            sl_n, tp_n = cv[i] - av[i] * ks, cv[i] + av[i] * kt
            le[i], pend, sl_sent[i], tp_sent[i], side[i], last = True, 1, sl_n, tp_n, 1, i
        elif sc[i]:
            sl_n, tp_n = cv[i] + av[i] * ks, cv[i] - av[i] * kt
            se[i], pend, sl_sent[i], tp_sent[i], side[i], last = True, -1, sl_n, tp_n, -1, i
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
