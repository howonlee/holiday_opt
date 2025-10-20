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

## Command Line Arguments

```
python holiday_opt.py [year] [num_voluntary_holidays]
```

- `year`: Year to optimize (default: current year)
- `num_voluntary_holidays`: Number of voluntary holidays to add (default: 5)

## License

MIT License - see LICENSE file for details
