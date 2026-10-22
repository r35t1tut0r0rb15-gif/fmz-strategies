"""Close crossings of the EMA 15 (up) or EMA 40 (down) with EMA 15 / 40 trend, previous-bar RSI 14 and MACD filters, hourly bars, from flat: the up-cross goes long and the down-cross goes short with a 1.2 ATR 14 stop from the signal close; 72 bars after the last signal the position is closed.
Port of FMZ strategy #488020 "Multi Indicator Confirmation Dynamic Trailing Breakout Quantitative Trading Strategy" (MomentumBreakout V1.2 - DOGE/USDT).

FMZ source id: 488020

Source
    https://www.fmz.com/strategy/488020 (PineScript v6, FMZ last modified 2025-03-24 14:20:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 231-311), EMA 15 / 40; ATR 14; RSI 14; MACD 12 / 26 / 9 (previous bar); stop 1.2 ATR; max hold 72 bars; risk 0.5 % sizing
    crossover(close, ema15) and ema15 > ema40 and rsi[1] > 50 and macd[1] > signal[1] and close > sma20 -> long stop := close - 1.2 atr, entry bar := bar
    crossunder(close, ema40) and ema15 < ema40 and atr > sma(atr, 14) -> short stop := close + 1.2 atr, entry bar := bar
    position and bar - entry bar >= 72 -> close all;  flat and signal -> entry + exit(stop = that stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "60" requests on the hourly chart are the chart itself, taken one bar back as written. The stop
      is sent once, with the entry, at the signal bar's level; the later ratchet of the variable is never
      re-sent, so the stop is fixed. The entry-bar counter is reset by every signal, held or not. Entries
      need a flat position at the bar's close, so a loop follows the stop on each bar's high / low (as
      #449508); the stop is sent as a fraction of the fill open (a level at or through it is marketable
      and closed one bar late, as #458256). Opposite entries cannot occur (entries only from flat). Stop
      module: portfolio_kwargs {} (driver D4). The risk-sized leveraged quantity is sizing. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR stop as a fraction of the fill; bar-count close.
    2 generic: PASS, EMA breakouts with RSI / MACD / ATR filters, ATR stop and time exit.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: risk-sized leveraged quantity and margins stored, not ported.
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

NAME = "fmz_488020_ema15_40_breakout_rsi_macd_atr_stop_72bar_exit_flat"
FAMILY = "ma_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "emaFast": [15, 10],
    "maxHoldBars": [72, 24],
}
DEFAULT_PARAMS = {"emaFast": 15, "maxHoldBars": 72, "emaSlow": 40, "atrPeriod": 14, "rsiPeriod": 14,
                  "macdFast": 12, "macdSlow": 26, "macdSignal": 9, "stop_atr": 1.2}


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

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    ef, es = ema(c, p["emaFast"]), ema(c, p["emaSlow"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atrPeriod"]))
    r1 = _rsi(c, int(p["rsiPeriod"])).shift(1)
    macd = ema(c, p["macdFast"]) - ema(c, p["macdSlow"])
    sig = ema(macd, p["macdSignal"])
    trend_up = (ef > es) & (r1 > 50) & (macd.shift(1) > sig.shift(1))
    lc = ((c > ef) & (pc <= ef.shift(1)) & trend_up & (c > c.rolling(20).mean())).to_numpy()
    sc = ((c < es) & (pc >= es.shift(1)) & (ef < es) & (atr > atr.rolling(14).mean())).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    av = atr.to_numpy() * float(p["stop_atr"])
    hold = int(p["maxHoldBars"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, side = np.full(m, np.nan), np.zeros(m)
    pos, pend, sl, sl_n, ebar = 0, 0, np.nan, np.nan, 0
    for i in range(m):
        if pend in (1, -1):
            pos, pend, sl = pend, 0, sl_n
            if (pos == 1 and sl >= ov[i]) or (pos == -1 and sl <= ov[i]):
                if pos == 1:                     # a level through the fill: closed at the next open
                    lx[i] = True
                else:
                    sx[i] = True
                pend = 2
        elif pend == 2:
            pos, pend = 0, 0
        if pos == 1 and pend == 0 and lv[i] <= sl:
            pos = 0                              # the stop fills inside this bar
        elif pos == -1 and pend == 0 and hv[i] >= sl:
            pos = 0
        if lc[i] or sc[i]:
            ebar = i
        if pos != 0 and pend == 0 and i - ebar >= hold:
            if pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pend = 2
            continue
        if pos != 0 or pend != 0:
            continue
        if lc[i] and not np.isnan(av[i]):
            sl_n = cv[i] - av[i]
            le[i], pend, sl_sent[i], side[i] = True, 1, sl_n, 1
        elif sc[i] and not np.isnan(av[i]):
            sl_n = cv[i] + av[i]
            se[i], pend, sl_sent[i], side[i] = True, -1, sl_n, -1
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, se, sx, sl_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, sd = sl_l.shift(1), sd.shift(1)    # the signal bar's level, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    return {"sl_stop": sl_f.where(sl_f > 0)}


def portfolio_kwargs(**params):
    return {}
