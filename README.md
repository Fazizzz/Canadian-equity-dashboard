# Canadian-equity-dashboard
TSX-focused time-series analytics tool that generates interactive HTML dashboards for Canadian equities. Computes core financial metrics including CAGR, annualized volatility, total return, and max drawdown using `yfinance` and `Plotly`. Built with modular design and reproducible Conda environment.

# Overview
This project provides a reproducible pipeline for:

* Retrieving historical TSX equity data

* Computing key return and risk metrics

* Visualizing time-series behavior in structured multi-panel dashboards

* Exporting standalone interactive HTML reports

As Canada continues to invest in domestic economic growth and infrastructure, the Toronto Stock Exchange (TSX) has seen strong performance across multiple sectors. This tool is designed specifically for TSX equities to support systematic, data-driven analysis of Canadian market opportunities. If a ticker is provided without a suffix (e.g., `RY`), `.TO` is appended automatically. Index symbols such as ^GSPTSE starting with a `^` are passed through unchanged.


## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Requirements](#requirements)
- [Repository Structure](#repository-structure)
- [Usage](#usage)
- [Output](#output)
- [Mathematical Definitions](#mathematical-definitions)
- [Design Decisions](#design-decisions)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [License](#license)
- [Acknowledgments](#acknowledgments)



## Installation
Clone this repository to your local machine and use the environment file to install dependencies:

```bash
git clone https://github.com/Fazizzz/Canadian-equity-dashboard.git

cd Canadian-equity-dashboard

conda env create -f environment.yml
conda activate canadian-equity-dashboard
```
Alternatively, you can use this as is if you have the relevant packages already installed.


## Requirements 

Dependencies:
  
* `python=3.11`
* `numpy`
* `pandas`
* `plotly`
* `yfinance`


## Repository Structure

```text
Canadian-equity-dashboard/
│
├── src/
│   ├── __init__.py
│   └── dashboard.py
│
├── scripts/
│   └── run_dashboard.py
│
├── outputs/ (generated HTML dashboards)
│
├── environment.yml
├── agent_spec.json
├── README.md
├── .gitignore
└── LICENSE

The `src/` directory contains the analytics engine.  
The `scripts/` directory provides the CLI interface.  
The `outputs/` directory stores generated dashboards and is excluded from version control.
```


## Usage

From the repository root:

```bash
python scripts/run_dashboard.py --ticker RY --period 5y
```
Parameters:

* `--ticker` : TSX ticker symbol (e.g., RY, ENB, SHOP.TO)

* `--period` : yfinance period string (e.g., 1y, 5y, max)

* `--out` : Optional custom output path

Example:

```bash
python scripts/run_dashboard.py --ticker ENB --period 1y
```


## Output


The tool generates a standalone interactive HTML dashboard containing:

1. Close price with 50D and 200D moving averages  
2. Volume  
3. Daily returns  
4. Rolling 30-day annualized volatility  

A summary annotation includes:

- Ticker
- Date range
- Total return
- CAGR
- Annualized volatility
- Maximum drawdown

If metrics cannot be computed due to insufficient data, warnings are emitted and values are displayed as `N/A`.

### Example Dashboard

![Figure1](https://github.com/Fazizzz/Canadian-equity-dashboard/blob/main/sample-outputs/Sample-output.png)

*Figure 1: TSX Composite Index (`^GSPTSE`, 1-year period) dashboard illustrating index-level price trend with 50-day and 200-day moving averages, trading volume, daily returns, and 30-day annualized rolling volatility. Summary statistics include total return, CAGR, annualized volatility, and maximum drawdown over the selected horizon.*


## Mathematical Definitions

- **Total Return**  
  (P_final / P_initial) − 1

- **CAGR**  
  (1 + Total Return)^(1 / years) − 1  
  where years = days / 365.25

- **Annualized Volatility**  
  std(daily_returns) × √252

- **Maximum Drawdown**  
  min((V_t / peak(V_t)) − 1)

Where 252 represents the approximate number of trading days per year.


## Design Decisions

- The tool is intentionally scoped to TSX equities.
- Tickers without suffix automatically append `.TO`.
- Index symbols beginning with `^` are not modified.
- Metrics emit warnings rather than crashing when insufficient data is available.
- The project separates analytics logic (`src/`) from CLI execution (`scripts/`) to maintain modularity.
- Conda environment ensures reproducibility.


## Limitations

- Only TSX equities are officially supported.
- Relies on data availability from yfinance.
- Does not currently support multi-ticker comparison or benchmarking.
- Not intended as investment advice.



## Future Improvements

- Optional benchmark comparison vs `^GSPTSE`
- Relative performance visualization
- Unit tests for metric validation
- Additional rolling risk statistics
- Agentic AI interface


## License

MIT License


## Acknowledgments

Muhammad Faizan Khalid — Author and current maintainer

This project was developed by Muhammad Faizan Khalid as part of a self-led portfolio initiative for ongoing professional development in data science, including coursework completed as part of an IBM Data Science Certification program. It is intended as an analytical utility for time-series financial data exploration and visualization.

This repository is provided for educational and demonstration purposes. It is not a commercial product and does not constitute financial or investment advice. The code is provided “as is,” without warranty of any kind. Please report bugs or issues through the repository for potential future improvements.

For citation or attribution, please reference:
Khalid, M. Faizan (or Khalid MF)

You can follow related research and professional updates via my [Google Scholar profile](https://scholar.google.com/citations?hl=en&user=qFZQ5wYAAAAJ&sortby=title&view_op=list_works&gmla=AL3_zigRWGX9g8Jc22idbBUMFuy7cVN_pEIyL6_DXSA-qWkJbcaONzhRNSmAwmQXKEm-3-WYGouZZC2pCE6zD9tZLxizbM7jQzzZMOgtkgsuL825u4lvSs9kwsccajhJbBg2Mrc37at_HCQ) or [Linkedin](https://www.linkedin.com/in/m-faizan-khalid/).
