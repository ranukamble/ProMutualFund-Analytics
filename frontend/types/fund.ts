export interface FundHolding {
  company_name: string;
  allocation_pct: number;
  sector?: string;
  asset_type?: string;
}

export interface FundOverview {
  scheme_code: string | number;
  scheme_name: string;
  fund_house?: string;
  category?: string;
  sub_category?: string;
  plan_type?: string;
  scheme_type?: string;
  isin?: string;
  rta?: string;
  rta_scheme_code?: string;
  launch_date?: string;
  benchmark?: string;
  rating?: number;
  risk_level?: string;
}

export interface LiveNavData {
  current_nav: number;
  nav_date: string;
  day_change?: number;
  currency?: string;
  "52_week_high"?: number;
  "52_week_low"?: number;
}

export interface FundFinancials {
  aum_in_crores?: number;
  aum_formatted?: string;
  expense_ratio?: number;
  expense_ratio_formatted?: string;
  base_expense_ratio?: string;
  turnover_ratio?: string;
  min_sip_amount?: number;
  min_lumpsum_amount?: number;
  min_additional_investment?: number;
  exit_load?: string;
}

export interface HistoricalReturns {
  return_1m?: string | number;
  return_3m?: string | number;
  return_6m?: string | number;
  return_1yr?: string | number;
  return_2yr?: string | number;
  return_3yr?: string | number;
  return_4yr?: string | number;
  return_5yr?: string | number;
  return_7yr?: string | number;
  return_10yr?: string | number;
  since_inception?: string | number;
}

export interface RiskMetrics {
  volatility_std_dev?: number;
  beta?: number;
  alpha?: number;
  sharpe_ratio?: number;
  sortino_ratio?: number;
  information_ratio?: number;
  max_drawdown?: number;
}

export interface FundSchemeDataset {
  status?: string;
  fund_overview: FundOverview;
  live_nav: LiveNavData;
  fund_financials?: FundFinancials;
  historical_returns_cagr?: HistoricalReturns;
  risk_and_volatility_metrics?: RiskMetrics;
  asset_allocation?: Record<string, number>;
  sector_allocation?: Record<string, number>;
  top_holdings?: FundHolding[];
}

export type VerificationStatus = "verified" | "discrepancy" | "outdated" | "error";

export interface FieldComparison {
  key: string;
  label: string;
  category: "NAV & Price" | "Financials" | "Returns (CAGR)" | "Risk & Volatility" | "Asset Allocation";
  provided: string | number | null | undefined;
  live: string | number | null | undefined;
  status: VerificationStatus;
  deltaPercent?: number | null;
  message: string;
}
