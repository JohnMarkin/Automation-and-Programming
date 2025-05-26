# VM-22 Life Contingent Annuity Rate Calculator (Non-Jumbo Contracts)

## Purpose
This tool calculates quarterly statutory maximum valuation interest rates under NAIC VM-22 for life-contingent, non-jumbo annuity contracts, based on Treasury yields, Table X (spreads), Table A (defaults), and prescribed weightings.

## Key Formula
I_q = R + S - D - E

Where:  
- R = Reference Rate (weighted average of U.S. Treasury yields)  
- S = Spread Rate (weighted average from Table X by WAL and credit rating)  
- D = Default Cost (weighted average from Table A by WAL and credit rating)  
- E = Spread Deduction (fixed at 0.25%)  

Final quarterly valuation interest rate:  
VM22 Rate = round[(R + S - D - E) * 4] / 4

## Inputs Required
1. Year (e.g., 2024)  
2. Quarter (e.g., 2)  

Followed by file uploads:
- Treasury Yields: CSV with “Date”, “2 Yr”, “5 Yr”, etc.  
- Table X: Spread rates by WAL and Moody’s rating  
- Table A: Default cost rates by WAL and Moody’s rating  
- Reference Rate Weights  
- Spread Rate Weights  
- Default Cost Weights  
- Daily Corporate Rates (optional)

## Class: `VM22_Calculator`

### Initialization
```python
calc = VM22_Calculator(year_input=2024, quarter_input=2)
```

### Method: `reference_rate()`
Calculates the reference rate using weighted Treasury yields.

### Method: `spread_rate()`
Calculates the weighted average spread from Table X.

### Method: `default_cost()`
Calculates the weighted default cost from Table A.

### Method: `VM22_Rates()`
Combines R, S, D and subtracts 0.0025, then annualizes and rounds.

## Expected Output
| Quarter | Bucket     | VM22 Quarterly Rate |
|---------|------------|---------------------|
| 2024Q2  | 0-4 Years  | 1.25%               |
| 2024Q2  | 5-9 Years  | 1.50%               |
| 2024Q2  | 10+ Years  | 1.75%               |

## Regulatory Notes
- Non-Jumbo Contracts: <$250M per plan, per insurer, within 90 days.  
- Reference Period: Quarter prior to valuation quarter.  
- Deduction: Fixed at 0.25% (0.0025 quarterly).  
- Rounding: Nearest multiple of 0.25%.

## Assumptions and Limitations
- Only for life contingent, non-jumbo products.  
- Assumes proper CSV formatting.  
- No UI beyond file uploads.  
- Future work: Jumbo handling, discount factor calc, visualization.