from datetime import date, timedelta

def test_allocation():
    today = date(2026, 6, 22)  # Monday
    deadline = date(2026, 6, 30)  # Tuesday next week (8 days duration)
    
    # 1. Available schedule (no weekend study)
    available_schedule = {
        "mon": True, "tue": True, "wed": True, "thu": True, "fri": True,
        "sat": False, "sun": False
    }
    
    WEEKDAY_MAP = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}
    
    def is_study_day(d: date) -> bool:
        day_key = WEEKDAY_MAP.get(d.weekday(), "")
        return bool(available_schedule.get(day_key, True))
        
    # 2. Collect all available study days from today to deadline
    all_study_days = []
    temp_date = today
    while temp_date <= deadline:
        if is_study_day(temp_date):
            all_study_days.append(temp_date)
        temp_date += timedelta(days=1)
        
    if not all_study_days:
        temp_date = today
        while temp_date <= deadline:
            all_study_days.append(temp_date)
            temp_date += timedelta(days=1)
            
    print(f"All study days from {today} to {deadline}:")
    for d in all_study_days:
        print(f"  - {d} (Weekday: {d.weekday()} - {WEEKDAY_MAP[d.weekday()]})")
        
    # 3. Dummy tasks (2 weeks, 5 tasks each = 10 tasks)
    all_tasks = []
    for week_num in [1, 2]:
        for task_idx in range(1, 6):
            all_tasks.append((week_num, f"Task {task_idx} of Week {week_num}"))
            
    num_tasks = len(all_tasks)
    num_days = len(all_study_days)
    
    print(f"\nAllocating {num_tasks} tasks over {num_days} study days:")
    for idx, (week_num, task) in enumerate(all_tasks):
        if num_tasks <= num_days:
            assigned_date = all_study_days[idx]
        else:
            day_idx = int(idx * num_days / num_tasks)
            day_idx = min(day_idx, num_days - 1)
            assigned_date = all_study_days[day_idx]
            
        print(f"  * {task} -> {assigned_date} ({WEEKDAY_MAP[assigned_date.weekday()]})")

if __name__ == "__main__":
    test_allocation()
