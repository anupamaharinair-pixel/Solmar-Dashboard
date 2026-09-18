# Solmar Eyewear — DTC Performance Dashboard

A Streamlit dashboard analyzing 109 weeks of Solmar Eyewear's direct-to-consumer revenue,
marketing spend, and promotional performance — built as a case study assignment.

## What it does

- **Dashboard tab** — 4-panel view of revenue trajectory & seasonality, paid media
  channel mix, new vs. repeat customer revenue split, and a BFCM vs. non-BFCM
  revenue/efficiency comparison.
- **Interpretation tab** — written analysis explaining what each panel shows and why it matters.
- **Recommendations tab** — concrete, data-backed suggestions for improving marketing
  efficiency and revenue growth.

## Key finding

BFCM (Black Friday/Cyber Monday) weeks generate ~3x the average weekly revenue of a
normal week, at a *higher* MER (marketing efficiency ratio) than the rest of the year —
meaning the lift isn't coming at the cost of efficiency. The recommendation is to test
applying similar promo intensity during the organic summer (May–Jul) demand peak.

## Tech stack

- Python, pandas
- Streamlit (app framework)
- Matplotlib / Seaborn (visualizations)

## Running it locally

```bash
pip install -r requirements.txt
streamlit run solmar_streamlit_app(1).py
```


## Author

Anupama Hari — MSc Statistics, CHRIST (Deemed to be University)
