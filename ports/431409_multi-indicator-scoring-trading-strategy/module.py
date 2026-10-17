"""Technicals rating of the open (Ichimoku, six Hull MAs, RSI, stochastic, CCI, MACD), broker days: a summed rating above
1.1 goes long, below -1.1 goes short; a 3 ATR stop and a 2 ATR trailing stop that starts after a set profit.
Port of FMZ strategy #431409 "Multi Indicator Scoring Trading Strategy" (Ichi HMA RSI Stoch CCI MACD Technicals Rating Strategy).

FMZ source id: 431409

Source
    https://www.fmz.com/strategy/431409 (PineScript v4, FMZ last modified 2023-11-07 16:16:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 200-319), source open, period 14, minimum strength 1.1, ATR exits 3 / 5 / 2
    ratingMA = mean of HMA ratings (HMA 14 / 20 / 30 / 50 / 100 / 200 of open vs open) and the Ichimoku rating
    ratingOther = mean of RSI 14, stoch 14 / 3 / 3, CCI 20 and MACD 12 / 26 / 9 ratings (all of open)
    ratingTotal = (ratingMA + ratingOther) / 2;  signal = ratingTotal + ratingOther + ratingMA
    signal > 1.1 -> entry long;  signal < -1.1 -> entry short
    exit(loss = 3 ATR, trail_points = 5 ATR, trail_offset = 2 ATR) (in ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The rating functions are ported line for line on the bar's open (known at its start), with the
      chart's own resolution (res ""). HMA = wma(2 wma(x, n / 2) - wma(x, n), round(sqrt n)).
    * The stop is 3 x the signal bar's ATR 14 as a fraction of its close (fixed at entry; the source
      re-sizes it with the current ATR). The trail is the house trail {"type": "volatility",
      "atr_n": 14, "k": 2, "anchor": "high_low", "activate_after": a} (Pine's trail follows the best
      high / low after trail_points of profit; the activation is a fraction of the fill price, as
      #427314, declared in the grid). Natively ported: mark trailing_stop.
    * Entries are re-issued on every qualifying bar; strategy.entry reverses: REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop and trail are house stops.
    2 generic: PASS, indicator ratings and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 50 % of equity and the commission stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_431409_technicals_rating"
FAMILY = "multi_indicator_vote"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "min_strength": [1.1, 0.7],
    "activate": [0.15, 0.05],
}
DEFAULT_PARAMS = {"period": 14, "min_strength": 1.1, "atr_len": 14, "sl_atr": 3.0, "trail_atr": 2.0,
                  "activate": 0.15}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: (a * w).sum() / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(round(np.sqrt(n))))


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _rate(buy, sell):
    return np.where(buy, 1.0, np.where(sell, -1.0, 0.0))


def _signal(bars_df, p):
    o, h, lo = bars_df["open"], bars_df["high"], bars_df["low"]
    pr = o

    def don(L):
        return (lo.rolling(L).min() + h.rolling(L).max()) / 2
    cl, bl = don(9), don(26)
    l1, l2 = (cl + bl) / 2, don(52)
    ma_sum = pd.Series(0.0, index=o.index)
    ma_cnt = pd.Series(0.0, index=o.index)
    for L in (int(p["period"]), 20, 30, 50, 100, 200):
        hm = _hma(pr, L)
        r = pd.Series(np.where(hm == pr, 0.0, np.where(hm < pr, 1.0, -1.0)), index=o.index)
        ok = hm.notna()
        ma_sum += r.where(ok, 0.0)
        ma_cnt += ok.astype(float)
    p1 = pr.shift(1)
    ic_ok = l1.notna() & l2.notna() & p1.notna() & bl.notna() & cl.notna()
    ic = _rate((l1 > l2) & (pr > l1) & (pr < bl) & (p1 < cl) & (pr > cl),
               (l2 > l1) & (pr < l2) & (pr > bl) & (p1 > cl) & (pr < cl))
    ma_sum += pd.Series(ic, index=o.index).where(ic_ok, 0.0)
    ma_cnt += ic_ok.astype(float)
    r_ma = (ma_sum / ma_cnt).where(ma_cnt > 0)
    rsi = _rsi(pr, 14)
    st = 100 * (pr - lo.rolling(14).min()) / (h.rolling(14).max() - lo.rolling(14).min()).replace(0.0, np.nan)
    ks = st.rolling(3).mean()
    ds = ks.rolling(3).mean()
    tp = pr.rolling(20).mean()
    md = pr.rolling(20).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    cci = (pr - tp) / (0.015 * md)
    macd = pr.ewm(span=12, adjust=False).mean() - pr.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    parts = [
        (rsi.notna() & rsi.shift(1).notna(),
         _rate((rsi < 30) & (rsi.shift(1) < rsi), (rsi > 70) & (rsi.shift(1) > rsi))),
        (ks.notna() & ds.notna() & ks.shift(1).notna() & ds.shift(1).notna(),
         _rate((ks < 20) & (ds < 20) & (ks > ds) & (ks.shift(1) < ds.shift(1)),
               (ks > 80) & (ds > 80) & (ks < ds) & (ks.shift(1) > ds.shift(1)))),
        (cci.notna() & cci.shift(1).notna(),
         _rate((cci < -100) & (cci > cci.shift(1)), (cci > 100) & (cci < cci.shift(1)))),
        (macd.notna() & sig.notna(), _rate(macd > sig, macd < sig)),
    ]
    o_sum = pd.Series(0.0, index=o.index)
    o_cnt = pd.Series(0.0, index=o.index)
    for ok, r in parts:
        o_sum += pd.Series(r, index=o.index).where(ok, 0.0)
        o_cnt += ok.astype(float)
    r_other = (o_sum / o_cnt).where(o_cnt > 0)
    total = ((r_ma + r_other) / 2).where(r_ma.notna())
    ts = total + r_other + r_ma
    ms = float(p["min_strength"])
    c = bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return (ts > ms).astype(bool), (ts < -ms).astype(bool), af


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh, _ = _signal(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signal(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_atr"]),
                      "anchor": "high_low", "activate_after": float(p["activate"])}}


def portfolio_kwargs(**params):
    return {}
