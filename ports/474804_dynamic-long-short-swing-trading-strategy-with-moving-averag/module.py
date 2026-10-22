"""EMA 20 / SMA 50 crossings with an RSI filter, daily bars: the cross up with RSI under 70 goes long, the cross down with RSI over 30 goes short; reversing. The 1.5 ATR stop and 3 ATR target are set from strategy.position_avg_price on the signal bar (na from flat, the replaced position's price on a reversal), as written.
Port of FMZ strategy #474804 "Dynamic Long Short Swing Trading Strategy with Moving Average Crossover Signal System" (Swing Trading Strategy with On/Off Long and Short).

FMZ source id: 474804

Source
    https://www.fmz.com/strategy/474804 (PineScript v5, FMZ last modified 2024-12-12 11:11:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-170), EMA 20 / SMA 50; RSI 14, 70 / 30; ATR 14: stop 1.5 x, target 3 x from avg; size by 1 % risk of a typed capital
    crossover(ema20, sma50) and rsi < 70 -> entry Long, exit(stop = avg - 1.5 atr, limit = avg + 3 atr);  crossunder and rsi > 30 -> entry Short, exit(stop = avg + 1.5 atr, limit = avg - 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are sent on the signal bar only, from strategy.position_avg_price, which is na from flat
      (no bracket) and the replaced position's fill price on a reversal, as written (as #468309,
      #473147), with the signal bar's ATR. The loop tracks the fill prices and the bracket inside each
      bar; the levels are sent as fractions of the new fill open (a level at or through it is marketable
      and closed one bar late). Crossings alternate, so no repeat signal re-sends it. Long and short both
      on (defaults). The risk-based size is not ported. REVERSAL INTENDED. Stop module: portfolio_kwargs
      {} (driver D4). Stops on daily bars: mark coarse_bar_stop. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the replaced position's price as the bracket base, as written.
    2 generic: PASS, EMA / SMA crossings with an RSI filter and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-based size from a typed capital stored, not ported.
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

NAME = "fmz_474804_ema20_sma50_cross_rsi_atr_bracket_from_replaced_avg"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [20, 10],
    "long_len": [50, 100],
}
DEFAULT_PARAMS = {"short_len": 20, "long_len": 50, "sl_atr": 1.5, "tp_atr": 3.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.rolling(int(p["long_len"])).mean()
    r = _rsi(c, 14)
    lc = ((a > b) & (a.shift(1) <= b.shift(1)) & (r < 70)).to_numpy()
    sc = ((a < b) & (a.shift(1) >= b.shift(1)) & (r > 30)).to_numpy()
    atr = _atr(bars_df, 14).to_numpy(dtype=float)
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    ks, kt = float(p["sl_atr"]), float(p["tp_atr"])
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
            sl_n, tp_n = avg - ks * atr[i], avg + kt * atr[i]   # na from flat
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i] and pos != -1:
            sl_n, tp_n = avg + ks * atr[i], avg - kt * atr[i]
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
