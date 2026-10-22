"""EMA 9 / 21 crossings on hlcc4 confirmed by the EMA 34, RSI 14, the bar colour and the MACD histogram, daily bars: confirmed cross ups go long and cross downs go short, from flat only, each with a 10-tick stop and target (0.001 ATR at the daily reading); a contrary signal closes the trade.
Port of FMZ strategy #454147 "EMA-RSI-MACD动态止盈止损交易策略-EMA-RSI-MACD-Dynamic-Take-Profit-and-Stop-Loss-Trading-Strategy" ([BUY/SELL]EMA RSI MACD with TP and SL).

FMZ source id: 454147

Source
    https://www.fmz.com/strategy/454147 (PineScript v5, FMZ last modified 2024-06-14 15:38:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-175), hlcc4 = (h + l + 2c) / 4; EMA 9 / 21 / 34; RSI 14 vs 50; MACD 12 / 26 / 9 histogram; TP / SL 10 pips x mintick
    cross up and hlcc4 > ema34 and rsi > 50 and close > open and hist > 0 -> (flat) entry Buy, exit(limit = close + 10 ticks, stop = close - 10 ticks)
    the mirror -> (flat) entry Sell;  open trade and a contrary signal -> close it

Interpretation choices (Pine rules in SURVEY_README.md)
    * All indicators run on hlcc4. Entries only from flat; a contrary signal only closes (the new
      entry's flat test fails on that bar). The 10-tick distances are 1.0 at the 0.1 tick, ported as
      ATR multiples at the daily reading (~1000): 0.001 ATR 14, from the bar before the fill, followed
      in the loop on each bar's high / low so the flat test lines up. Opposite entries cannot occur
      (entries only from flat). Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark
      coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick bracket as ATR multiples.
    2 generic: PASS, multi-confirmed EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_454147_hlcc4_ema_cross_rsi_macd_tick_bracket_from_flat"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.001, 1.0],
    "ema3_len": [34, 50],
}
DEFAULT_PARAMS = {"k_atr": 0.001, "ema3_len": 34, "atr_len": 14, "rsi_len": 14, "rsi_mid": 50.0}


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
    return 100 - 100 / (1 + up / dn)


def _atr_frac(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n)) / c


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    x = (h + lo + c + c) / 4
    e1, e2 = x.ewm(span=9, adjust=False).mean(), x.ewm(span=21, adjust=False).mean()
    e3 = x.ewm(span=int(p["ema3_len"]), adjust=False).mean()
    r = _rsi(x, int(p["rsi_len"]))
    macd = x.ewm(span=12, adjust=False).mean() - x.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    mid = float(p["rsi_mid"])
    buy = ((e1 > e2) & (e1.shift(1) <= e2.shift(1)) & (x > e3) & (r > mid) & (c > o) & (hist > 0)).to_numpy()
    sell = ((e1 < e2) & (e1.shift(1) >= e2.shift(1)) & (x < e3) & (r < mid) & (c < o) & (hist < 0)).to_numpy()
    fr = (float(p["k_atr"]) * _atr_frac(bars_df, p["atr_len"])).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pend, fi, k = 0, 0, -1, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, fi, k = pend, i, fr[i - 1]
        elif pend == 2:
            pos = 0
        pend = 0
        if pos != 0 and (lv[i] <= ov[fi] * (1 - k) or hv[i] >= ov[fi] * (1 + k)):
            pos = 0                              # the stop or target fills inside the bar
        if pos == 1 and sell[i]:
            lx[i], pend = True, 2
        elif pos == -1 and buy[i]:
            sx[i], pend = True, 2
        elif pos == 0 and i + 1 < m:
            if buy[i]:
                le[i], pend = True, 1
            elif sell[i]:
                se[i], pend = True, -1
    return le, lx, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in _run(bars_df, p))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["k_atr"]) * _atr_frac(bars_df, p["atr_len"])
    return {"sl_stop": a.shift(1), "tp_stop": a.shift(1)}


def portfolio_kwargs(**params):
    return {}
