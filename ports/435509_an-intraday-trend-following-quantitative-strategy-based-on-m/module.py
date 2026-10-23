"""Broker days, long only: the script's own parabolic SAR (start 1.02, step 1.02, maximum 1.2) in a downtrend with the RSI 50 above 49, the ADX 14 above its EMA 10 and the Chaikin money flow 20 above 0 goes long; the SAR in an uptrend with the RSI under 49, the ADX under its EMA and the money flow under 0 closes.
Port of FMZ strategy #435509 "An Intraday Trend Following Quantitative Strategy Based on Multi indicator Condition Filtering" (psar+ adx + cmf + rsi Strategy).

FMZ source id: 435509

Source
    https://www.fmz.com/strategy/435509 (PineScript v4, FMZ last modified 2023-12-15 15:59:37).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 165-266), SAR start 1.02, increment 1.02, maximum 1.2; RSI 50, middle 49; CMF 20; ADX 14 / DI 14; EMA 10 of the ADX
    the TradingView sample SAR (uptrend / EP / AF state, SAR clamped to the last two lows or highs);  long = not uptrend and rsi(50) > 49 and adx > ema(adx, 10) and cmf > 0 -> entry long
    short = uptrend and rsi < 49 and adx < ema(adx, 10) and cmf < 0 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SAR is the script's own loop with its inputs, so its acceleration starts above 1 (1.02) and is
      capped at 1.2: the SAR overshoots the extreme point every bar (weird case); ported as written. The
      trend state is na on the first bar. The ADX is the classic DMI / ADX (fixnan on the DI lines). The
      money flow is a ratio of volume sums. Long only. 100 % of equity and the commission are sizing and
      costs. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR, RSI, ADX and money-flow agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 1000, commission 0.1 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Chaikin money flow 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435509_custom_sar_rsi50_adx_cmf_agreement_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [50, 14],
    "lengthCMF": [20, 50],
}
DEFAULT_PARAMS = {"start": 1.02, "increment": 1.02, "maximum": 1.2, "rsi_len": 50, "middle": 49.0,
                  "lengthCMF": 20, "adx_len": 14, "di_len": 14, "ema_len": 10}


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _adx(h, lo, c, di_len, adx_len):
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, di_len)
    plus, minus = _fixnan(100 * _rma(pdm, di_len) / atr), _fixnan(100 * _rma(mdm, di_len) / atr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


def _script_sar(hv, lv, cv, start, inc, mx):
    """The script's own SAR loop; returns the uptrend state per bar (NaN on the first bar)."""
    m = len(cv)
    up_state = np.full(m, np.nan)
    uptrend, ep, sar, af, nxt = None, np.nan, np.nan, start, np.nan
    for i in range(1, m):
        first = False
        sar = nxt
        if i == 1:
            if cv[1] > cv[0]:
                uptrend, ep, psar, pep = True, hv[1], lv[0], hv[1]
            else:
                uptrend, ep, psar, pep = False, lv[1], hv[0], lv[1]
            first = True
            sar = psar + start * (pep - psar)
        if uptrend:
            if sar > lv[i]:
                first, uptrend, sar, ep, af = True, False, max(ep, hv[i]), lv[i], start
        else:
            if sar < hv[i]:
                first, uptrend, sar, ep, af = True, True, min(ep, lv[i]), hv[i], start
        if not first:
            if uptrend:
                if hv[i] > ep:
                    ep, af = hv[i], min(af + inc, mx)
            else:
                if lv[i] < ep:
                    ep, af = lv[i], min(af + inc, mx)
        if uptrend:
            sar = min(sar, lv[i - 1])
            if i > 1:
                sar = min(sar, lv[i - 2])
        else:
            sar = max(sar, hv[i - 1])
            if i > 1:
                sar = max(sar, hv[i - 2])
        nxt = sar + af * (ep - sar)
        up_state[i] = 1.0 if uptrend else 0.0
    return up_state


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    ups = _script_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                      float(p["start"]), float(p["increment"]), float(p["maximum"]))
    rsi = _rsi(c, int(p["rsi_len"]))
    ad = pd.Series(np.where(((c == h) & (c == lo)) | (h == lo), 0.0,
                            (2 * c - lo - h) / (h - lo).where(h != lo)), index=c.index) * v
    n = int(p["lengthCMF"])
    sv = v.rolling(n).sum()
    mf = ad.rolling(n).sum() / sv.where(sv != 0)
    adx = _adx(h, lo, c, int(p["di_len"]), int(p["adx_len"]))
    ae = adx.ewm(span=int(p["ema_len"]), adjust=False).mean()
    mid = float(p["middle"])
    long_c = (ups == 0.0) & (rsi > mid).to_numpy() & (adx > ae).to_numpy() & (mf > 0).to_numpy()
    short_c = (ups == 1.0) & (rsi < mid).to_numpy() & (adx < ae).to_numpy() & (mf < 0).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and long_c[i]:
            le[i], pos = True, 1
        elif pos == 1 and short_c[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
