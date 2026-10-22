"""Two SMA crossing pairs with RSI extremes and four entry ids, daily bars: a 9 / 21 cross up with the RSI over 70 goes short ("Venda Curta"), a cross down under 30 goes long ("Compra Curta"); a 25 / 99
cross up over 70 goes long ("Compra Forte"), a cross down under 30 short ("Venda Forte"); each id closes on its pair's opposite cross; reversing.
Port of FMZ strategy #449955 "移动平均线与RSI综合交易策略-Moving-Average-and-RSI-Comprehensive-Trading-Strategy" (Estratégia-Médias Móveis (por Svitorino_trade)).

FMZ source id: 449955

Source
    https://www.fmz.com/strategy/449955 (PineScript v5, FMZ last modified 2024-04-30 16:31:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 125-185), SMA 9 / 21 and 25 / 99 (hand-written); RSI 14, levels 30 / 70
    x921 up and rsi > 70 -> entry Venda Curta (short);  x921 down and rsi < 30 -> entry Compra Curta (long);  x921 up -> close Compra Curta;  x921 down -> close Venda Curta
    x2599 up and rsi > 70 -> entry Compra Forte (long);  x2599 down and rsi < 30 -> entry Venda Forte (short);  x2599 up -> close Venda Forte;  x2599 down -> close Compra Forte

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calls run in the script's order with one position (pyramiding 1): an entry on the side
      already held or ordered that bar is ignored; a close acts only on the id held into the bar and
      not reversed by that bar's entries; when a close and a new same-side entry meet on one bar the
      position is kept under the new id. The 9 / 21 pair trades against the cross (short on a cross
      up), as written. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, two SMA crossing pairs with RSI extremes, id-specific closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449955_two_sma_pairs_rsi_extreme_four_ids_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "ob": [70.0, 60.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "ob": 70.0, "os": 30.0, "l1": 9, "l2": 21, "l3": 25, "l4": 99}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a1, a2, a3, a4 = (c.rolling(int(p[k])).mean() for k in ("l1", "l2", "l3", "l4"))
    up1 = ((a1 > a2) & (a1.shift(1) <= a2.shift(1))).to_numpy()
    dn1 = ((a1 < a2) & (a1.shift(1) >= a2.shift(1))).to_numpy()
    up2 = ((a3 > a4) & (a3.shift(1) <= a4.shift(1))).to_numpy()
    dn2 = ((a3 < a4) & (a3.shift(1) >= a4.shift(1))).to_numpy()
    r = _rsi(c, int(p["rsi_len"])).to_numpy()
    ob, os_ = float(p["ob"]), float(p["os"])
    m = len(up1)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    hd, hid = 0, None
    with np.errstate(invalid="ignore"):
        for i in range(m):
            cd, cid = hd, hid
            calls = [
                ("e", up1[i] and r[i] > ob, "Venda Curta", -1),
                ("e", dn1[i] and r[i] < os_, "Compra Curta", 1),
                ("c", up1[i], "Compra Curta", 0),
                ("c", dn1[i], "Venda Curta", 0),
                ("e", up2[i] and r[i] > ob, "Compra Forte", 1),
                ("e", dn2[i] and r[i] < os_, "Venda Forte", -1),
                ("c", up2[i], "Venda Forte", 0),
                ("c", dn2[i], "Compra Forte", 0),
            ]
            for kind, on, name, d in calls:
                if not on:
                    continue
                if kind == "e":
                    if cd != d:
                        cd, cid = d, name
                elif hid == name and cd == hd and cid == hid:
                    cd, cid = 0, None          # a close acts only on the id held into the bar
            if cd != hd:
                if cd == 1:
                    le[i] = True
                elif cd == -1:
                    se[i] = True
                elif hd == 1:
                    lx[i] = True
                else:
                    sx[i] = True
            hd, hid = cd, cid
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
