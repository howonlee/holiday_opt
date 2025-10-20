# Holiday Optimizer

A Python tool that finds the optimal voluntary holidays to optimize your time off by minimizing the total "days-until-next-holiday" metric across the entire year.

## Installation

No installation required beyond Python 3.6+. The script uses only standard library modules.

## Usage

### Basic Usage

Run with defaults (current year, 5 voluntary holidays):
```bash
python holiday_opt.py
```

### Specify Year

```bash
python holiday_opt.py 2025
```

### Specify Year and Number of Voluntary Holidays

```bash
python holiday_opt.py 2025 7
```

### Example Output

```
Year: 2025, Voluntary Holidays: 5

=== Holiday Optimization for 2025 ===

Fixed holidays (9):
  - New Year's Day: 2025-01-01 (Wed)
  - MLK Day: 2025-01-20 (Mon)
  - Memorial Day: 2025-05-26 (Mon)
  - Independence Day: 2025-07-04 (Fri)
  - Labor Day: 2025-09-01 (Mon)
  - Thanksgiving Day: 2025-11-27 (Thu)
  - Day After Thanksgiving: 2025-11-28 (Fri)
  - Christmas Eve: 2025-12-24 (Wed)
  - Christmas Day: 2025-12-25 (Thu)

Baseline total days-until-holiday: 18250

Searching for best 5 voluntary holiday(s)...
Algorithm: Greedy (fast approximation)

======================================================================

Optimal voluntary holidays:
  - 2025-02-14 (Fri)
  - 2025-04-04 (Fri)
  - 2025-06-06 (Fri)
  - 2025-08-01 (Fri)
  - 2025-10-03 (Fri)

Results:
  Baseline total:      18250 days
  Optimized total:     15532 days
  Improvement:         2718 days (14.9%)
  Average days/day:    42.55
```

## Command Line Arguments

```
python holiday_opt.py [year] [num_voluntary_holidays]
```

- `year`: Year to optimize (default: current year)
- `num_voluntary_holidays`: Number of voluntary holidays to add (default: 5)

## License

MIT License - see LICENSE file for details
