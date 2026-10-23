"""Broker days: three long set-ups on above-average volume (an RSI 14 dip under 35 in an EMA 50 / ADX > 25 trend, an RSI dip under 35 inside the 20-day range, a close over the prior 20-day closing high with a rising price-volume line) and one short set-up (RSI over 65 inside the range); a repeated signal while in a trade arms a 1.2 ATR stop and a 3.6 ATR target from the fill price, followed in the signals; reversing.
Port of FMZ strategy #471721 "Multi Strategy Adaptive Trend Following and Breakout Trading System" (Ceulemans Trading Bot met ADX, Trendfilter en Selecteerbare Strategieen).

FMZ source id: 471721

Source
    https://www.fmz.com/strategy/471721 (PineScript v5, FMZ last modified 2024-11-12 16:43:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 128-194), EMA 50; RSI 14, 35 / 65; ATR 14; DMI 14 / 14, ADX > 25; volume SMA 20; stop 1.2 ATR, target 3 x 1.2 ATR
    isTrending and isOversold and volumeFilter -> entry "Koop Trend", exit("Exit Trend", stop = position_avg_price - 1.2 atr, limit = position_avg_price + 3.6 atr)
    isRange and rsi < 35 and volumeFilter -> entry "Koop Range" + exit;  isRange and rsi > 65 and volumeFilter -> entry "Short Range" + exit(stop = avg + 1.2 atr, limit = avg - 3.6 atr)
    isBreakout (close > highest(close[1], 20) and obv > cum(change(close[20]) x volume)) and volumeFilter -> entry "Koop Breakout" + exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits have no from_entry and take their levels from position_avg_price at the call: on a bar
      that opens a trade from flat the price is na, so no exit exists; only a signal repeated while in a
      trade arms its exit, from the held trade's fill and that bar's ATR (each exit id keeps its latest
      levels; any hit closes). Exits sent on a reversal bar are taken to act on the new trade (with the
      old trade's price, as written); earlier ones end with their trade. The house engine cannot arm a
      bracket later, so the signals follow it: a bar whose low / high reaches an armed level closes the
      trade at the next open (mark trailing_stop_pending). Default pyramiding: one trade at a time; a
      later call wins on a two-sided bar. obv is the cumulative price change x volume, as written.
      REVERSAL INTENDED. Capital-risk input unused. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; late-armed ATR bracket followed in the signals.
    2 generic: PASS, trend dips, range reversals and volume breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (capital-risk input unused).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20 and in the price-volume lines; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_471721_trend_range_breakout_volume_late_atr_bracket_reversal"
FAMILY = "multi_setup"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sl_mult": [1.2, 2.0],
    "rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"ema_len": 50, "len": 20, "os": 35.0, "ob": 65.0, "sl_mult": 1.2, "rr": 3.0}


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
    """Pine fixnan: a NaN takes the last non-NaN value (Pine's own indicator semantics)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _dmi(h, lo, c, n, sm):
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trur = _rma(tr, n)
    plus, minus = _fixnan(100 * _rma(pdm, n) / trur), _fixnan(100 * _rma(mdm, n) / trur)
    tot = plus + minus
    adx = 100 * _rma((plus - minus).abs() / tot.where(tot != 0, 1.0), sm)
    return plus, minus, adx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["len"])
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, 14)
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    _, _, adx = _dmi(h, lo, c, 14, 14)
    obv = (c.diff() * v).fillna(0.0).cumsum()
    obv_lag = (c.shift(n).diff() * v).fillna(0.0).cumsum()
    vf = v > v.rolling(n).mean()
    trending = (c > ema) & (adx > 25)
    in_range = ~trending & (c < c.rolling(n).max()) & (c > c.rolling(n).min())
    breakout = (c > pc.rolling(n).max()) & (obv > obv_lag)
    os_, ob_ = float(p["os"]), float(p["ob"])
    calls = [((trending & (r < os_) & vf).to_numpy(), 1, "trend"),
             ((in_range & (r < os_) & vf).to_numpy(), 1, "range_l"),
             ((in_range & (r > ob_) & vf).to_numpy(), -1, "range_s"),
             ((breakout & vf).to_numpy(), 1, "breakout")]
    on, hn, ln = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    an = atr.to_numpy(dtype=float)
    sl_k, tp_k = float(p["sl_mult"]), float(p["sl_mult"]) * float(p["rr"])
    m = len(on)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine, fp, pend = 0, 0, np.nan, False
    armed = {}
    for i in range(m):
        held = pine
        if pend:                           # the strategy's own position (re)opened at this open
            fp, pend = on[i], False
        if held != 0 and armed:
            for st, lm in armed.values():  # the exit trades against the held side, whatever its formula
                if (held == 1 and (ln[i] <= st or hn[i] >= lm)) or (held == -1 and (hn[i] >= st or ln[i] <= lm)):
                    held = 0
                    break
            if held == 0:
                armed, fp = {}, np.nan
        new, sent = held, {}
        for cond, d, key in calls:
            if cond[i]:
                new = d
                if held != 0:              # position_avg_price is na when flat: no exit exists
                    a = an[i]
                    if d == 1:
                        sent[key] = (fp - sl_k * a, fp + tp_k * a)
                    else:
                        sent[key] = (fp + sl_k * a, fp - tp_k * a)
        if new != held:
            armed, pend = {k: lv for k, lv in sent.items()}, new != 0
        else:
            armed.update(sent)
        pine = new
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif vpos == 1:
                lx[i] = True
            else:
                sx[i] = True
            vpos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
