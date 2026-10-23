"""Broker days: swing highs / lows 50 bars back that stand above / below every later bar mark structure; a close above the latest swing high flips the structure up, below the latest swing low down; a close above the flip bar's high in an up-structure with RSI 14 under 30 on volume over 1.2 x its 20-day average goes long, the mirror short; each trade gets a 2 ATR stop and 3 ATR target from the signal close; reversing.
Port of FMZ strategy #488545 "Market Structure Swing Trading Strategy" (Market Structure Swing Trading).

FMZ source id: 488545

Source
    https://www.fmz.com/strategy/488545 (PineScript v5, FMZ last modified 2025-03-28 17:38:45).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 101-198), swing length 50; RSI 14 (70 / 30); volume SMA 20 x 1.2; ATR 14 x 2 / 3; 5 % of equity
    top = high[50] > highest(50) ? high[50] : na;  btm = low[50] < lowest(50) ? low[50] : na;  top -> topy := top, top_crossed := false;  close > topy and not top_crossed -> os := 1, top_crossed := true  (btm mirrored, os := 0)
    os != os[1] -> max := high, min := low;  longEntry = close > max and os == 1 and rsi < 30 and highVolume -> entry Long, exit(stop = close - 2 atr, limit = close + 3 atr);  short mirrored (os == 0, rsi > 70)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.highest(50) / ta.lowest(50) use the high / low of the last 50 bars including the current one, so
      a swing is a bar 50 bars back above (below) all 50 later bars. max / min are the high / low of the
      bar where the structure flipped and stay fixed until the next flip. The long needs an up-structure
      breakout with RSI under 30 (and the short RSI over 70), which rarely meet (weird case). The bracket is
      sent on signal bars as levels from that close: ported as fractions of the fill, exact (1e-6 floor).
      REVERSAL INTENDED. 5 % of equity is sizing. Stop module: portfolio_kwargs {} (driver D4). Stops on
      1-day bars: coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, change-of-character structure breaks with RSI and volume filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 5 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.2 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_488545_choch_bos_rsi_volume_atr_bracket_reversal"
FAMILY = "market_structure"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "swing_len": [50, 20],
    "rsi_os": [30.0, 40.0],
}
DEFAULT_PARAMS = {"swing_len": 50, "rsi_os": 30.0, "vol_mult": 1.2, "sl_atr": 2.0, "tp_atr": 3.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n = int(p["swing_len"])
    top = h.shift(n).where(h.shift(n) > h.rolling(n).max()).to_numpy(dtype=float)
    btm = lo.shift(n).where(lo.shift(n) < lo.rolling(n).min()).to_numpy(dtype=float)
    r = _rsi(c, 14).to_numpy(dtype=float)
    hv = (v > v.rolling(20).mean() * float(p["vol_mult"])).to_numpy()
    cn, hn, ln = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    os_lvl = float(p["rsi_os"])
    m = len(cn)
    buy, sell = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    topy = btmy = np.nan
    tc = bc = False
    os_, prev_os = 0, 0
    mx = mn = np.nan
    for i in range(m):
        if not np.isnan(top[i]) and top[i] != 0:
            topy, tc = top[i], False
        if not np.isnan(btm[i]) and btm[i] != 0:
            btmy, bc = btm[i], False
        if cn[i] > topy and not tc:
            os_, tc = 1, True
        if cn[i] < btmy and not bc:
            os_, bc = 0, True
        if i > 0 and os_ != prev_os:
            mx, mn = hn[i], ln[i]
        buy[i] = cn[i] > mx and os_ == 1 and r[i] < os_lvl and hv[i]
        sell[i] = cn[i] < mn and os_ == 0 and r[i] > 100 - os_lvl and hv[i]
        prev_os = os_
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy, index=ix), false, pd.Series(sell, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    atr = _atr(bars_df, 14)
    sl_d, tp_d = float(p["sl_atr"]) * atr, float(p["tp_atr"]) * atr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
