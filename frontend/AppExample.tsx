import React from "react";
import { FundLiveVerifier } from "./components/FundLiveVerifier";
import { FundSchemeDataset } from "./types/fund";

// Example Parag Parikh Flexi Cap Fund Dataset
const sampleDataset: FundSchemeDataset = {
  fund_overview: {
    scheme_code: "122639",
    scheme_name: "Parag Parikh Flexi Cap Fund - Direct Plan - Growth",
    fund_house: "PPFAS Mutual Fund",
    category: "Equity",
    sub_category: "Flexi Cap",
    plan_type: "Direct",
    scheme_type: "Growth",
    isin: "INF879O01027",
    benchmark: "NIFTY 500 Total Return Index (TRI)",
    rating: 4,
    risk_level: "Very High"
  },
  live_nav: {
    current_nav: 90.3546,
    nav_date: "19-Oct-2026",
    day_change: -0.58,
    "52_week_high": 95.7732,
    "52_week_low": 82.0594
  },
  fund_financials: {
    aum_in_crores: 145070.5,
    aum_formatted: "₹1,45,070.50 Cr",
    expense_ratio: 0.69,
    expense_ratio_formatted: "0.69%",
    min_sip_amount: 1000,
    exit_load: "2% if redeemed within 365 days; 1% between 365-730 days. Nil after 730 days."
  },
  historical_returns_cagr: {
    return_1yr: "-4.42%",
    return_3yr: "12.37%",
    return_5yr: "10.31%",
    since_inception: "17.83%"
  },
  asset_allocation: {
    "Domestic Equity": 68.12,
    "Foreign Equity": 14.39,
    "Real Estate (REITs)": 6.27,
    "Cash & Money Market": 11.22
  },
  top_holdings: [
    { company_name: "HDFC Bank Ltd", allocation_pct: 7.75, sector: "Financial Services" },
    { company_name: "Power Grid Corp of India", allocation_pct: 5.60, sector: "Energy & Utilities" },
    { company_name: "ITC Ltd", allocation_pct: 5.49, sector: "Consumer Staples" },
    { company_name: "Coal India Ltd", allocation_pct: 5.39, sector: "Materials" },
    { company_name: "ICICI Bank Ltd", allocation_pct: 5.24, sector: "Financial Services" },
    { company_name: "Alphabet Inc (Google)", allocation_pct: 4.29, sector: "Technology" }
  ]
};

export const AppExample: React.FC = () => {
  return (
    <div className="w-full min-h-screen">
      <FundLiveVerifier
        dataset={sampleDataset}
        defaultTheme="dark"
        onVerified={(results: any) => {
          console.log("Verification finished with results:", results);
        }}
      />
    </div>
  );
};

export default AppExample;
