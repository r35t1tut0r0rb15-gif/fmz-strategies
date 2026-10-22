"""EMA 10 / 25 crossings on the EMA 50 side with DI+ over 25, RSI 14 on the 50 side and the close beyond its SMA 14, broker days: the cross up goes long, the cross down goes short, each with a 1.5 ATR stop and 2 ATR target from the signal close; reversing.
Port of FMZ strategy #478706 "Triple EMA Trend Following Multi Indicator Quantitative Trading Strategy" (Daily Strategy with Triple EMA, DMI, DPO, RSI, and ATR).

FMZ source id: 478706

Source
    https://www.fmz.com/strategy/478706 (PineScript v5, FMZ last modified 2025-01-17 14:57:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-174), EMA 10 / 25 / 50; DMI 14 / 14 (outputs misnamed); DPO 14 (close - SMA 14); RSI 14; ATR 14 x 1.5 / 2.0; 100 % of equity
    [adx, diPlus, diMinus] = ta.dmi(14, 14) (Pine returns [di+, di-, adx]);  crossover(ema10, ema25) and both > ema50 and adx > 25 and rsi > 50 and dpo > 0 -> entry Buy + exit(stop = close - 1.5 atr, limit = close + 2 atr);  mirror -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.dmi returns [DI+, DI-, ADX], so the script's "adx" is DI+, and both sides require DI+ over 25,
      as written. The bracket is sent once, on the signal bar, from its close and ATR: sent as fractions of
      the fill open (a level at or through it is marketable and closed one bar late, as #458256); the
      crossings alternate, so no repeat re-sends it. REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). Stops on daily bars: mark coarse_bar_stop. The 100 % of equity size and risk input are
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ
      = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with DI+, RSI and DPO filters and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and risk 2 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_478706_ema10_25_cross_ema50_diplus_rsi_dpo_atr_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 2.5],
    "tp_mult": [2.0, 4.0],
}
DEFAULT_PARAMS = {"atr_mult": 1.5, "tp_mult": 2.0, "dmi_length": 14, "dpo_length": 14, "rsi_length": 14, "atr_length": 14}


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _dmi(b, n):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    return plus, minus, adx


def _signals(bars_df, p):
    c = bars_df["close"]
    f, m_, s = (c.ewm(span=n, adjust=False).mean() for n in (10, 25, 50))
    di_plus = _dmi(bars_df, int(p["dmi_length"]))[0]          # the script's "adx"
    dpo = c - c.rolling(int(p["dpo_length"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    le = (f > m_) & (f.shift(1) <= m_.shift(1)) & (f > s) & (m_ > s) & (di_plus > 25) & (r > 50) & (dpo > 0)
    se = (f < m_) & (f.shift(1) >= m_.shift(1)) & (f < s) & (m_ < s) & (di_plus > 25) & (r < 50) & (dpo < 0)
    atr = _atr(bars_df, p["atr_length"])
    sl, tp = float(p["atr_mult"]) * atr, float(p["tp_mult"]) * atr
    lvl = {"l_sl": c - sl, "l_tp": c + tp, "s_sl": c + sl, "s_tp": c - tp}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
