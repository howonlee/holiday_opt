#!/usr/bin/env python3
"""
Holiday Optimizer Script
Finds the optimal voluntary holidays to minimize the total sum of days-until-holiday
across all days in a year
"""

from datetime import datetime, timedelta
import sys
from itertools import combinations
from bisect import bisect_left


def get_nth_weekday_of_month(year, month, weekday, n):
    """Get the nth occurrence of a weekday in a month"""
    date = datetime(year, month, 1)
    count = 0

    while count < n:
        if date.weekday() == weekday:
            count += 1
            if count == n:
                return date
        date += timedelta(days=1)
    return date


def get_last_weekday_of_month(year, month, weekday):
    """Get the last occurrence of a weekday in a month"""
    # Start from last day of month
    if month == 12:
        date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        date = datetime(year, month + 1, 1) - timedelta(days=1)

    while date.weekday() != weekday:
        date -= timedelta(days=1)
    return date


def get_holidays(year):
    """Get all holidays for a given year

    Returns:
        Tuple of (name, date) tuples, sorted by date
    """
    # Define holidays (weekday: 0=Monday, 4=Thursday)
    holidays = [
        ("New Year's Day", datetime(year, 1, 1)),
        ("MLK Day", get_nth_weekday_of_month(year, 1, 0, 3)),  # 3rd Monday in January
        ("President's Day", get_nth_weekday_of_month(year, 2, 0, 3)),  # 3rd Monday in February
        ("Memorial Day", get_last_weekday_of_month(year, 5, 0)),  # Last Monday in May
        ("Juneteenth", datetime(year, 6, 19)),
        ("Independence Day", datetime(year, 7, 4)),
        ("Labor Day", get_nth_weekday_of_month(year, 9, 0, 1)),  # 1st Monday in September
        ("Thanksgiving Day", get_nth_weekday_of_month(year, 11, 3, 4)),  # 4th Thursday in November
    ]

    # Day after Thanksgiving
    thanksgiving = get_nth_weekday_of_month(year, 11, 3, 4)
    holidays.append(("Day After Thanksgiving", thanksgiving + timedelta(days=1)))

    # Christmas holidays
    holidays.extend([
        ("Christmas Eve", datetime(year, 12, 24)),
        ("Christmas Day", datetime(year, 12, 25))
    ])

    # Return sorted tuple (immutable)
    return tuple(sorted(holidays, key=lambda x: x[1]))


def days_until_next_holiday(current_date, holiday_dates_only):
    """Calculate days until the next holiday using binary search

    Args:
        current_date: The date to check from
        holiday_dates_only: Sorted sequence of holiday datetime objects only (no names)

    Returns:
        Number of days until next holiday
    """
    idx = bisect_left(holiday_dates_only, current_date)

    if idx < len(holiday_dates_only):
        return (holiday_dates_only[idx] - current_date).days

    # If no holiday found this year, get first holiday of next year
    next_year_holidays = get_holidays(current_date.year + 1)
    first_holiday_date = next_year_holidays[0][1]
    return (first_holiday_date - current_date).days


def precompute_days_until_holiday(year, holiday_dates_only):
    """Precompute days-until-holiday for each day of the year

    This is much faster than calculating on-demand for repeated evaluations.

    Returns:
        Tuple of integers representing days-until-holiday for each day
    """
    days_list = []
    current_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    while current_date <= end_date:
        days = days_until_next_holiday(current_date, holiday_dates_only)
        days_list.append(days)
        current_date += timedelta(days=1)

    return tuple(days_list)


def calculate_total_days_until_holiday(year, holidays):
    """Calculate the sum of days-until-holiday for every day of the year"""
    holiday_dates_only = tuple(sorted(date for _, date in holidays))
    days_list = precompute_days_until_holiday(year, holiday_dates_only)
    return sum(days_list)


def generate_candidate_dates(year):
    """Generate all possible dates in a year as candidates for voluntary holidays

    Returns:
        Tuple of datetime objects
    """
    candidates = []
    current_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    while current_date <= end_date:
        candidates.append(current_date)
        current_date += timedelta(days=1)

    return tuple(candidates)


def calculate_impact_of_adding_holiday(year, baseline_days_list, new_holiday_date):
    """Calculate the improvement in total if we add a new holiday

    Uses the precomputed baseline to incrementally calculate the change.

    Args:
        year: The year
        baseline_days_list: Precomputed sequence of days-until-holiday for each day
        new_holiday_date: The proposed new holiday date

    Returns:
        The reduction in total days (positive means improvement)
    """
    improvement = 0
    new_holiday_ordinal = (new_holiday_date - datetime(year, 1, 1)).days

    # For each day before this holiday, check if it would be closer than current next holiday
    for day_offset in range(len(baseline_days_list)):
        current_days_until = baseline_days_list[day_offset]
        days_to_new_holiday = new_holiday_ordinal - day_offset

        # If this new holiday is closer than the current next holiday
        if 0 <= days_to_new_holiday < current_days_until:
            improvement += current_days_until - days_to_new_holiday

    return improvement


def find_best_next_holiday(year, baseline_days_list, candidates, already_selected):
    """Find the single best holiday to add next

    Args:
        year: The year
        baseline_days_list: Current precomputed days-until-holiday list
        candidates: All possible candidate dates
        already_selected: Set of already selected dates

    Returns:
        Tuple of (best_candidate, improvement) or (None, 0) if none found
    """
    best_candidate = None
    best_improvement = 0

    for candidate in candidates:
        if candidate in already_selected:
            continue

        improvement = calculate_impact_of_adding_holiday(
            year, baseline_days_list, candidate
        )

        if improvement > best_improvement:
            best_improvement = improvement
            best_candidate = candidate

    return (best_candidate, best_improvement)


def find_optimal_voluntary_holidays_greedy(year, num_voluntary_holidays, fixed_holidays):
    """Find good voluntary holidays using a greedy algorithm

    This doesn't guarantee the global optimum but finds a very good solution quickly.

    Returns:
        Tuple of datetime objects representing the selected voluntary holidays
    """
    fixed_holiday_dates = frozenset(date for _, date in fixed_holidays)
    candidates = tuple(
        date for date in generate_candidate_dates(year)
        if date not in fixed_holiday_dates
    )

    # Start with baseline
    current_holidays = fixed_holidays
    holiday_dates_only = tuple(sorted(date for _, date in current_holidays))
    baseline_days_list = precompute_days_until_holiday(year, holiday_dates_only)

    selected = []

    for _ in range(num_voluntary_holidays):
        best_candidate, _ = find_best_next_holiday(
            year, baseline_days_list, candidates, frozenset(selected)
        )

        if best_candidate:
            selected.append(best_candidate)
            # Create new holiday list for next iteration (immutable pattern)
            current_holidays = tuple(current_holidays) + (("Voluntary Holiday", best_candidate),)
            holiday_dates_only = tuple(sorted(date for _, date in current_holidays))
            baseline_days_list = precompute_days_until_holiday(year, holiday_dates_only)

    return tuple(selected)


def find_optimal_voluntary_holidays_exhaustive(year, num_voluntary_holidays, fixed_holidays, candidates):
    """Find optimal holidays using exhaustive search

    Returns:
        Tuple of (best_combination, best_total, total_combinations_checked)
    """
    baseline_total = calculate_total_days_until_holiday(year, fixed_holidays)
    best_combination = tuple()
    best_total = baseline_total

    combinations_list = list(combinations(candidates, num_voluntary_holidays))
    total_combinations = len(combinations_list)

    for combo in combinations_list:
        # Create holiday list with voluntary holidays added (immutable)
        test_holidays = tuple(fixed_holidays) + tuple((f"Voluntary Holiday", date) for date in combo)
        test_holidays = tuple(sorted(test_holidays, key=lambda x: x[1]))

        total = calculate_total_days_until_holiday(year, test_holidays)

        if total < best_total:
            best_total = total
            best_combination = combo

    return (best_combination, best_total, total_combinations)


def compute_optimization_result(year, num_voluntary_holidays, use_greedy=True):
    """Compute the optimal voluntary holidays

    Returns:
        Dictionary containing all optimization results
    """
    fixed_holidays = get_holidays(year)
    fixed_holiday_dates = frozenset(date for _, date in fixed_holidays)

    # Generate candidate dates (exclude existing holidays)
    candidates = tuple(
        date for date in generate_candidate_dates(year)
        if date not in fixed_holiday_dates
    )

    # Calculate baseline (without voluntary holidays)
    baseline_total = calculate_total_days_until_holiday(year, fixed_holidays)

    if use_greedy:
        best_combination = find_optimal_voluntary_holidays_greedy(
            year, num_voluntary_holidays, fixed_holidays
        )
        total_combinations = None
    else:
        best_combination, _, total_combinations = find_optimal_voluntary_holidays_exhaustive(
            year, num_voluntary_holidays, fixed_holidays, candidates
        )

    # Calculate final total with best combination
    final_holidays = tuple(fixed_holidays) + tuple(("Voluntary Holiday", date) for date in best_combination)
    final_holidays = tuple(sorted(final_holidays, key=lambda x: x[1]))
    best_total = calculate_total_days_until_holiday(year, final_holidays)

    improvement = baseline_total - best_total
    improvement_pct = (improvement / baseline_total) * 100 if baseline_total > 0 else 0

    return {
        "year": year,
        "fixed_holidays": fixed_holidays,
        "num_voluntary_holidays": num_voluntary_holidays,
        "baseline_total": baseline_total,
        "best_combination": tuple(sorted(best_combination)),
        "best_total": best_total,
        "improvement": improvement,
        "improvement_pct": improvement_pct,
        "average_days_per_day": best_total / 365,
        "use_greedy": use_greedy,
        "total_combinations": total_combinations,
    }


def format_optimization_report(result):
    """Format optimization results as a string

    Args:
        result: Dictionary from compute_optimization_result

    Returns:
        Formatted string report
    """
    lines = []

    lines.append(f"\n=== Holiday Optimization for {result['year']} ===\n")
    lines.append(f"Fixed holidays ({len(result['fixed_holidays'])}):")
    for name, date in result['fixed_holidays']:
        lines.append(f"  - {name}: {date.strftime('%Y-%m-%d (%a)')}")

    lines.append(f"\nBaseline total days-until-holiday: {result['baseline_total']}")
    lines.append(f"\nSearching for best {result['num_voluntary_holidays']} voluntary holiday(s)...")

    algorithm_name = 'Greedy (fast approximation)' if result['use_greedy'] else 'Exhaustive (slow but optimal)'
    lines.append(f"Algorithm: {algorithm_name}\n")

    if result['total_combinations'] is not None:
        lines.append(f"Evaluated {result['total_combinations']:,} combinations...")

    lines.append(f"\n{'=' * 70}")
    lines.append(f"\nOptimal voluntary holidays:")
    for date in result['best_combination']:
        lines.append(f"  - {date.strftime('%Y-%m-%d (%a)')}")

    lines.append(f"\nResults:")
    lines.append(f"  Baseline total:      {result['baseline_total']} days")
    lines.append(f"  Optimized total:     {result['best_total']} days")
    lines.append(f"  Improvement:         {result['improvement']} days ({result['improvement_pct']:.1f}%)")
    lines.append(f"  Average days/day:    {result['average_days_per_day']:.2f}")

    return '\n'.join(lines)


def find_optimal_voluntary_holidays(year, num_voluntary_holidays, use_greedy=True):
    """Find the best voluntary holidays and print results

    This is the main entry point that handles I/O (impure wrapper around pure functions)

    Args:
        year: The year to optimize
        num_voluntary_holidays: Number of voluntary holidays to add
        use_greedy: If True, use fast greedy algorithm; if False, use exhaustive search

    Returns:
        Tuple of (best_combination, best_total)
    """
    result = compute_optimization_result(year, num_voluntary_holidays, use_greedy)
    report = format_optimization_report(result)
    print(report)

    return (result['best_combination'], result['best_total'])


if __name__ == "__main__":
    year = datetime.now().year
    num_voluntary = 5  # Default number of voluntary holidays

    # Parse command line arguments
    if len(sys.argv) > 1:
        year = int(sys.argv[1])
    if len(sys.argv) > 2:
        num_voluntary = int(sys.argv[2])

    print(f"Year: {year}, Voluntary Holidays: {num_voluntary}")

    find_optimal_voluntary_holidays(year, num_voluntary)
