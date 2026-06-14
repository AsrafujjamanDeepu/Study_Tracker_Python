from graphics import Canvas


CANVAS_WIDTH = 390
CANVAS_HEIGHT = 760

DEFAULT_SUBJECTS = ["English", "Math", "ICT", "Others"]
COLOR_PALETTE = ["blue", "green", "purple", "orange", "red"]
SUBJECTS = DEFAULT_SUBJECTS[:]

FIRE = "\U0001f525"
PARTY = "\U0001f389"
WARNING = "\u26a0"
MEDAL = "\U0001f3c5"
LOCK = "\U0001f512"
SAD = "\U0001f622"
TARGET = "\U0001f3af"

sessions = []
buttons = []

current_screen = "dashboard"
current_day = 1
daily_goal = 4.0
exam_name = "Exam"
exam_days_left = 60

selected_subject_index = 0
form_hours = 2
form_minutes = 30
notice = ""


def main():
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    draw_current_screen(canvas)

    while True:
        x, y = get_click(canvas)
        action = get_button_action(x, y)

        if action is not None:
            keep_running = handle_action(action)
            if not keep_running:
                break
            draw_current_screen(canvas)


def handle_action(action):
    global current_screen, selected_subject_index, form_hours, form_minutes
    global daily_goal, current_day, exam_days_left, notice

    notice = ""

    if action == "exit":
        return False
    elif action == "dashboard":
        current_screen = "dashboard"
    elif action == "add":
        current_screen = "add"
    elif action == "stats":
        current_screen = "stats"
    elif action == "report":
        current_screen = "report"
    elif action == "add_subject":
        add_new_subject()
    elif action == "delete_subject":
        delete_selected_subject()
    elif action == "subject_previous":
        selected_subject_index = (selected_subject_index - 1) % len(SUBJECTS)
    elif action == "subject_next":
        selected_subject_index = (selected_subject_index + 1) % len(SUBJECTS)
    elif action == "hours_down":
        form_hours = max(0, form_hours - 1)
    elif action == "hours_up":
        form_hours = min(12, form_hours + 1)
    elif action == "minutes_down":
        form_minutes = max(0, form_minutes - 5)
    elif action == "minutes_up":
        form_minutes = min(55, form_minutes + 5)
    elif action == "goal_down":
        daily_goal = max(0.5, daily_goal - 0.5)
    elif action == "goal_up":
        daily_goal = min(12, daily_goal + 0.5)
    elif action == "exam_down":
        exam_days_left = max(0, exam_days_left - 1)
    elif action == "exam_up":
        exam_days_left += 1
    elif action == "next_day":
        current_day += 1
        exam_days_left = max(0, exam_days_left - 1)
        notice = "Moved to Day " + str(current_day) + "."
    elif action == "reset":
        reset_tracker()
    elif action == "save_session":
        save_session_from_form()

    return True


def reset_tracker():
    global SUBJECTS, sessions, current_screen, current_day, daily_goal, exam_days_left
    global selected_subject_index, form_hours, form_minutes, notice

    SUBJECTS = DEFAULT_SUBJECTS[:]
    sessions = []
    current_screen = "dashboard"
    current_day = 1
    daily_goal = 4.0
    exam_days_left = 60
    selected_subject_index = 0
    form_hours = 2
    form_minutes = 30
    notice = "Tracker reset. All project data erased."


def add_new_subject():
    global selected_subject_index, notice

    print("\nADD SUBJECT")
    new_subject = input("Enter new subject name: ").strip()

    if new_subject == "":
        notice = "Subject was not added."
        return

    if len(new_subject) > 18:
        new_subject = new_subject[:18]

    existing_index = get_subject_index(new_subject)

    if existing_index != -1:
        selected_subject_index = existing_index
        notice = "Subject already exists: " + SUBJECTS[existing_index] + "."
        return

    SUBJECTS.append(new_subject)
    selected_subject_index = len(SUBJECTS) - 1
    notice = "Subject added: " + new_subject + "."


def delete_selected_subject():
    global sessions, selected_subject_index, notice

    if len(SUBJECTS) <= 1:
        notice = "You must keep at least one subject."
        return

    subject = SUBJECTS[selected_subject_index]
    new_sessions = []
    removed_sessions = 0

    for session in sessions:
        if session["subject"] == subject:
            removed_sessions += 1
        else:
            new_sessions.append(session)

    sessions = new_sessions
    SUBJECTS.pop(selected_subject_index)

    if selected_subject_index >= len(SUBJECTS):
        selected_subject_index = len(SUBJECTS) - 1

    notice = "Deleted " + subject + " and " + str(removed_sessions) + " session(s)."


def save_session_from_form():
    global current_screen, notice

    minutes = form_hours * 60 + form_minutes

    if minutes <= 0:
        notice = "Choose a duration before saving."
        return

    subject = SUBJECTS[selected_subject_index]
    sessions.append({
        "subject": subject,
        "minutes": minutes,
        "day": current_day,
    })

    notice = "Saved " + format_duration(minutes) + " for " + subject + "."
    current_screen = "dashboard"


def draw_current_screen(canvas):
    if current_screen == "add":
        draw_add_session_screen(canvas)
    elif current_screen == "stats":
        draw_stats_screen(canvas)
    elif current_screen == "report":
        draw_report_screen(canvas)
    else:
        draw_dashboard(canvas)


def draw_dashboard(canvas):
    reset_screen(canvas)
    draw_header(canvas, "STUDY TRACKER")

    x, width = get_content_box()
    y = 76

    draw_rect(canvas, x, y, x + width, y + 170, "lightgray")
    draw_text(canvas, x + 14, y + 14, "Today's Goal: " + format_goal(daily_goal), 15, "black")
    draw_button(canvas, x + width - 132, y + 10, 58, 28, "- Goal", "goal_down", 11, "blue")
    draw_button(canvas, x + width - 68, y + 10, 58, 28, "+ Goal", "goal_up", 11, "blue")

    goal_percent = get_goal_percent()
    draw_text(canvas, x + 14, y + 48, "Progress: " + str(round(goal_percent)) + "%", 14, "black")
    draw_progress_bar(canvas, x + 14, y + 74, width - 28, 22, goal_percent, "green")
    draw_text(
        canvas,
        x + 14,
        y + 105,
        format_hours(get_today_minutes()) + " / " + format_goal(daily_goal) + " Completed",
        13,
        "black",
    )

    if goal_percent >= 100:
        draw_text(canvas, x + 14, y + 130, PARTY + " Daily Goal Achieved!", 14, "green")
    else:
        draw_text(canvas, x + 14, y + 130, "Streak: " + str(get_current_streak()) + " Days " + FIRE, 14, "black")

    badge_count = str(get_unlocked_badge_count()) + " / " + str(len(get_badges()))
    draw_text(canvas, x + 14, y + 152, "Total Hours: " + format_hours(get_total_minutes()), 13, "black")
    draw_text(canvas, x + 192, y + 152, "Badges: " + badge_count, 13, "black")

    draw_button(canvas, x, y + 188, width, 42, "Add Session", "add", 16, "green")
    draw_button(canvas, x, y + 238, width, 38, "Next Day", "next_day", 14, "blue")

    if notice != "":
        draw_text(canvas, x, y + 286, notice, 12, "green")

    chart_y = y + 326
    draw_text(canvas, x, chart_y - 26, "Subject Hours", 17, "black")
    chart_height = draw_compact_subject_rows(canvas, x, chart_y, width)

    weak_y = chart_y + chart_height + 16
    draw_weak_subject_detector(canvas, x, weak_y, width)

    draw_bottom_nav(canvas, "dashboard")


def draw_add_session_screen(canvas):
    reset_screen(canvas)
    draw_header(canvas, "ADD SESSION")

    x, width = get_content_box()
    y = 90

    draw_rect(canvas, x, y, x + width, y + 466, "lightgray")
    draw_text(canvas, x + 14, y + 16, "Day " + str(current_day), 15, "black")

    draw_text(canvas, x + 14, y + 54, "Subject", 15, "black")
    draw_button(canvas, x + 14, y + 82, 44, 42, "<", "subject_previous", 18, "blue")
    draw_rect(canvas, x + 66, y + 82, x + width - 66, y + 124, "white")
    draw_centered_text(canvas, x + 66, y + 82, x + width - 66, y + 124, SUBJECTS[selected_subject_index], 16, "black")
    draw_button(canvas, x + width - 58, y + 82, 44, 42, ">", "subject_next", 18, "blue")

    draw_button(canvas, x + 14, y + 136, width - 28, 34, "Delete This Subject", "delete_subject", 13, "red")
    draw_button(canvas, x + 14, y + 178, width - 28, 34, "Add New Subject", "add_subject", 14, "blue")

    draw_text(canvas, x + 14, y + 236, "Hours", 15, "black")
    draw_stepper(canvas, x + 14, y + 262, width - 28, str(form_hours), "hours_down", "hours_up")

    draw_text(canvas, x + 14, y + 330, "Minutes", 15, "black")
    draw_stepper(canvas, x + 14, y + 356, width - 28, str(form_minutes), "minutes_down", "minutes_up")

    draw_button(canvas, x + 14, y + 408, width - 28, 44, "Save", "save_session", 16, "green")

    if notice != "":
        draw_text(canvas, x, y + 488, notice, 12, "green")

    progress_y = y + 526
    draw_text(canvas, x, progress_y - 24, "Daily Goal Progress", 17, "black")
    draw_progress_bar(canvas, x, progress_y, width, 24, get_goal_percent(), "green")
    draw_text(
        canvas,
        x,
        progress_y + 34,
        format_hours(get_today_minutes()) + " / " + format_goal(daily_goal) + " Completed",
        13,
        "black",
    )

    draw_bottom_nav(canvas, "add")


def draw_stats_screen(canvas):
    reset_screen(canvas)
    draw_header(canvas, "SUBJECT STATS")

    x, width = get_content_box()
    y = 88

    draw_text(canvas, x, y - 26, "Subject Statistics", 18, "black")
    chart_height = draw_subject_bar_chart(canvas, x, y, width, get_subject_minutes())

    weak_y = y + chart_height + 22
    weak_height = draw_weak_subject_detector(canvas, x, weak_y, width)

    badge_y = weak_y + weak_height + 12
    draw_badges(canvas, x, badge_y, width)

    draw_bottom_nav(canvas, "stats")


def draw_report_screen(canvas):
    reset_screen(canvas)
    draw_header(canvas, "WEEKLY REPORT")

    x, width = get_content_box()
    y = 88

    weekly_stats = get_weekly_subject_minutes()
    weekly_total = get_weekly_minutes()
    goal_completion = get_weekly_goal_completion()

    draw_rect(canvas, x, y, x + width, y + 244, "lightgray")
    draw_text(canvas, x + 14, y + 16, "Total Hours: " + format_hours(weekly_total), 15, "black")

    if weekly_total > 0:
        most_subjects = get_subjects_with_most_hours(weekly_stats)
        least_subjects = get_subjects_with_least_hours(weekly_stats)
        most_hours = weekly_stats[most_subjects[0]]
        least_hours = weekly_stats[least_subjects[0]]
        most_lines = make_comma_lines(most_subjects, 34, 2)
        least_lines = make_comma_lines(least_subjects, 34, 2)

        draw_text(canvas, x + 14, y + 48, "Most Studied:", 13, "black")
        draw_subject_result(canvas, x + 14, y + 72, most_lines, most_hours, "green")
        draw_text(canvas, x + 14, y + 118, "Least Studied:", 13, "black")
        draw_subject_result(canvas, x + 14, y + 142, least_lines, least_hours, "red")
    else:
        draw_text(canvas, x + 14, y + 70, "No study sessions this week.", 14, "gray")

    draw_text(canvas, x + 14, y + 188, "Goal Completion: " + str(round(goal_completion)) + "%", 13, "black")
    draw_progress_bar(canvas, x + 14, y + 212, width - 28, 22, goal_completion, "green")

    streak_y = y + 274
    draw_rect(canvas, x, streak_y, x + width, streak_y + 106, "lightgray")

    current_streak = get_current_streak()
    if current_streak == 0 and len(sessions) > 0:
        draw_text(canvas, x + 14, streak_y + 16, "Streak Broken " + SAD, 15, "red")
    else:
        draw_text(canvas, x + 14, streak_y + 16, "Current Streak: " + str(current_streak) + " Days " + FIRE, 15, "black")

    draw_text(canvas, x + 14, streak_y + 48, "Longest Streak: " + str(get_longest_streak()) + " Days", 14, "black")
    draw_text(canvas, x + 14, streak_y + 78, "Current Day: " + str(current_day), 13, "black")

    exam_y = streak_y + 132
    draw_rect(canvas, x, exam_y, x + width, exam_y + 106, "lightgray")
    draw_text(canvas, x + 14, exam_y + 16, TARGET + " " + exam_name, 14, "black")
    draw_text(canvas, x + 14, exam_y + 46, "Days Remaining: " + str(exam_days_left), 14, "purple")
    draw_button(canvas, x + 14, exam_y + 70, 95, 28, "Exam -", "exam_down", 12, "blue")
    draw_button(canvas, x + 122, exam_y + 70, 95, 28, "Exam +", "exam_up", 12, "blue")
    draw_button(canvas, x + 230, exam_y + 70, width - 244, 28, "Next Day", "next_day", 12, "green")

    draw_bottom_nav(canvas, "report")


def draw_header(canvas, title):
    x, width = get_content_box()
    draw_text(canvas, x, 18, title, 24, "black")
    subtitle = "Day " + str(current_day) + " | " + exam_name + ": " + str(exam_days_left) + " days"
    draw_text(canvas, x, 48, subtitle, 12, "gray")


def draw_bottom_nav(canvas, active):
    x, width = get_content_box()
    y = CANVAS_HEIGHT - 52
    gap = 6
    button_width = int((width - gap * 3) / 4)

    nav_items = [
        ("Home", "dashboard"),
        ("Stats", "stats"),
        ("Report", "report"),
        ("Reset", "reset"),
    ]

    for i in range(len(nav_items)):
        label, action = nav_items[i]
        left = x + i * (button_width + gap)
        if action == "reset":
            color = "red"
            text_color = "white"
        else:
            color = "blue" if active == action else "lightgray"
            text_color = "white" if active == action else "black"
        draw_button(canvas, left, y, button_width, 42, label, action, 11, color, text_color)


def draw_stepper(canvas, x, y, width, value, down_action, up_action):
    draw_button(canvas, x, y, 48, 44, "-", down_action, 20, "blue")
    draw_rect(canvas, x + 58, y, x + width - 58, y + 44, "white")
    draw_centered_text(canvas, x + 58, y, x + width - 58, y + 44, value, 18, "black")
    draw_button(canvas, x + width - 48, y, 48, 44, "+", up_action, 20, "blue")


def draw_subject_result(canvas, x, y, subject_lines, minutes, color):
    if len(subject_lines) == 1:
        draw_text(canvas, x, y, subject_lines[0] + " (" + format_hours(minutes) + ")", 14, color)
    else:
        draw_text(canvas, x, y, subject_lines[0], 14, color)
        draw_text(canvas, x, y + 20, subject_lines[1] + " (" + format_hours(minutes) + ")", 14, color)


def draw_compact_subject_rows(canvas, x, y, width):
    stats = get_subject_minutes()
    max_minutes = max(stats.values())
    if max_minutes == 0:
        max_minutes = 1

    row_height = get_subject_row_height(210, 32)

    for i in range(len(SUBJECTS)):
        subject = SUBJECTS[i]
        minutes = stats[subject]
        top = y + i * row_height
        draw_text(canvas, x, top + 2, shorten_text(subject, 10), 12, "black")
        bar_x = x + 82
        value_x = x + width - 58
        bar_width = value_x - bar_x - 8
        fill_width = int(bar_width * minutes / max_minutes)
        draw_rect(canvas, bar_x, top + 5, bar_x + bar_width, top + 21, "white")
        if fill_width > 0:
            draw_rect(canvas, bar_x, top + 5, bar_x + fill_width, top + 21, get_subject_color(subject))
        draw_text(canvas, value_x, top + 2, format_hours(minutes), 12, "black")

    return len(SUBJECTS) * row_height


def draw_subject_bar_chart(canvas, x, y, width, stats):
    max_minutes = max(stats.values())
    if max_minutes == 0:
        max_minutes = 1

    row_height = get_subject_row_height(320, 54)

    for i in range(len(SUBJECTS)):
        subject = SUBJECTS[i]
        minutes = stats[subject]
        top = y + i * row_height
        draw_text(canvas, x, top, shorten_text(subject, 18), 14, "black")
        draw_rect(canvas, x, top + 24, x + width, top + 42, "lightgray")
        fill_width = int(width * minutes / max_minutes)
        if fill_width > 0:
            draw_rect(canvas, x, top + 24, x + fill_width, top + 42, get_subject_color(subject))
        draw_text(canvas, x + width - 62, top, format_hours(minutes), 13, "black")

    return len(SUBJECTS) * row_height


def draw_weak_subject_detector(canvas, x, y, width):
    stats = get_subject_minutes()
    total = sum(stats.values())

    draw_rect(canvas, x, y, x + width, y + 92, "lightgray")
    draw_text(canvas, x + 14, y + 10, WARNING + " Weak Subject Detector", 14, "black")

    if total == 0:
        draw_text(canvas, x + 14, y + 42, "No study data yet.", 13, "gray")
        return 92

    weak_subjects = get_weak_subjects(stats)

    if len(weak_subjects) == 0:
        draw_text(canvas, x + 14, y + 42, "Your subjects look balanced.", 13, "green")
        return 92

    weak_lines = make_comma_lines(weak_subjects, 34, 2)
    draw_text(canvas, x + 14, y + 38, "Neglecting: " + weak_lines[0], 13, "red")

    if len(weak_lines) > 1:
        draw_text(canvas, x + 14, y + 62, weak_lines[1], 13, "red")

    return 92


def draw_badges(canvas, x, y, width):
    badges = get_badges()

    draw_text(canvas, x, y - 24, "Achievement Badges", 17, "black")

    for i in range(len(badges)):
        name, unlocked = badges[i]
        top = y + i * 28
        color = "yellow" if unlocked else "lightgray"
        icon = MEDAL if unlocked else LOCK
        draw_rect(canvas, x, top, x + width, top + 23, color)
        draw_text(canvas, x + 10, top + 4, icon + " " + name, 12, "black")


def draw_progress_bar(canvas, x, y, width, height, percent, color):
    percent = max(0, min(percent, 100))
    draw_rect(canvas, x, y, x + width, y + height, "white")
    fill_width = int(width * percent / 100)

    if fill_width > 0:
        draw_rect(canvas, x, y, x + fill_width, y + height, color)


def draw_button(canvas, x, y, width, height, label, action, size=14, color="blue", text_color="white"):
    draw_rect(canvas, x, y, x + width, y + height, color)
    draw_centered_text(canvas, x, y, x + width, y + height, label, size, text_color)

    buttons.append({
        "x1": x,
        "y1": y,
        "x2": x + width,
        "y2": y + height,
        "action": action,
    })


def draw_centered_text(canvas, x1, y1, x2, y2, text, size, color):
    estimated_width = len(text) * size * 0.54
    x = x1 + ((x2 - x1) - estimated_width) / 2
    y = y1 + ((y2 - y1) - size) / 2
    draw_text(canvas, x, y, text, size, color)


def reset_screen(canvas):
    global buttons
    buttons = []
    draw_rect(canvas, 0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, "white")


def get_content_box():
    width = min(CANVAS_WIDTH - 32, 560)
    x = int((CANVAS_WIDTH - width) / 2)
    return x, width


def get_subject_index(subject_name):
    for i in range(len(SUBJECTS)):
        if SUBJECTS[i].lower() == subject_name.lower():
            return i

    return -1


def get_subject_color(subject):
    index = get_subject_index(subject)

    if index == -1:
        return COLOR_PALETTE[0]

    return COLOR_PALETTE[index % len(COLOR_PALETTE)]


def get_subject_row_height(max_height, normal_height):
    if len(SUBJECTS) == 0:
        return normal_height

    return min(normal_height, max(22, int(max_height / len(SUBJECTS))))


def get_weak_subjects(stats):
    total = sum(stats.values())

    if total == 0 or len(stats) == 0:
        return []

    average = total / len(stats)
    weak_subjects = []

    for subject in SUBJECTS:
        if stats[subject] <= average * 0.65:
            weak_subjects.append(subject)

    return weak_subjects


def make_comma_lines(items, max_length, max_lines):
    lines = []
    current_line = ""

    for item in items:
        if current_line == "":
            next_line = item
        else:
            next_line = current_line + ", " + item

        if len(next_line) <= max_length:
            current_line = next_line
        else:
            lines.append(current_line)
            current_line = item

            if len(lines) == max_lines:
                lines[-1] = shorten_text(lines[-1] + ", ...", max_length)
                return lines

    if current_line != "":
        lines.append(current_line)

    return lines


def shorten_text(text, max_length):
    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


def get_total_minutes():
    total = 0

    for session in sessions:
        total += session["minutes"]

    return total


def get_today_minutes():
    total = 0

    for session in sessions:
        if session["day"] == current_day:
            total += session["minutes"]

    return total


def get_weekly_minutes():
    total = 0

    for session in get_weekly_sessions():
        total += session["minutes"]

    return total


def get_subject_minutes():
    stats = {}

    for subject in SUBJECTS:
        stats[subject] = 0

    for session in sessions:
        subject = session["subject"]
        if subject not in stats:
            stats[subject] = 0
        stats[subject] += session["minutes"]

    return stats


def get_weekly_subject_minutes():
    stats = {}

    for subject in SUBJECTS:
        stats[subject] = 0

    for session in get_weekly_sessions():
        subject = session["subject"]
        if subject not in stats:
            stats[subject] = 0
        stats[subject] += session["minutes"]

    return stats


def get_weekly_sessions():
    first_day = current_day - 6
    weekly_sessions = []

    for session in sessions:
        if first_day <= session["day"] <= current_day:
            weekly_sessions.append(session)

    return weekly_sessions


def get_studied_days():
    studied_days = []

    for session in sessions:
        if session["day"] not in studied_days:
            studied_days.append(session["day"])

    return studied_days


def get_current_streak():
    studied_days = get_studied_days()
    streak = 0
    day = current_day

    while day in studied_days:
        streak += 1
        day -= 1

    return streak


def get_longest_streak():
    studied_days = sorted(get_studied_days())

    if len(studied_days) == 0:
        return 0

    longest = 1
    current = 1

    for i in range(1, len(studied_days)):
        if studied_days[i] == studied_days[i - 1] + 1:
            current += 1
        else:
            current = 1

        if current > longest:
            longest = current

    return longest


def get_goal_percent():
    if daily_goal <= 0:
        return 0

    return min(100, get_today_minutes() / (daily_goal * 60) * 100)


def get_weekly_goal_completion():
    if daily_goal <= 0:
        return 0

    days_in_report = min(7, current_day)
    weekly_goal = daily_goal * 60 * days_in_report
    return min(100, get_weekly_minutes() / weekly_goal * 100)


def get_most_subject(stats):
    best_subject = SUBJECTS[0]

    for subject in stats:
        if stats[subject] > stats[best_subject]:
            best_subject = subject

    return best_subject


def get_subjects_with_most_hours(stats):
    most_subjects = []
    highest_minutes = None

    for subject in SUBJECTS:
        minutes = stats[subject]

        if highest_minutes is None or minutes > highest_minutes:
            highest_minutes = minutes
            most_subjects = [subject]
        elif minutes == highest_minutes:
            most_subjects.append(subject)

    return most_subjects


def get_least_subject(stats):
    weakest_subject = SUBJECTS[0]

    for subject in stats:
        if stats[subject] < stats[weakest_subject]:
            weakest_subject = subject

    return weakest_subject


def get_subjects_with_least_hours(stats):
    least_subjects = []
    lowest_minutes = None

    for subject in SUBJECTS:
        minutes = stats[subject]

        if lowest_minutes is None or minutes < lowest_minutes:
            lowest_minutes = minutes
            least_subjects = [subject]
        elif minutes == lowest_minutes:
            least_subjects.append(subject)

    return least_subjects


def join_subjects(subjects):
    text = ""

    for i in range(len(subjects)):
        if i == 0:
            text = subjects[i]
        else:
            text += ", " + subjects[i]

    return text


def get_badges():
    total = get_total_minutes()
    streak = get_current_streak()

    return [
        ("First Study Session", len(sessions) >= 1),
        ("7 Day Streak", streak >= 7),
        ("100 Study Hours", total >= 100 * 60),
        ("30 Day Streak", streak >= 30),
        ("60 Day Streak", streak >= 60),
    ]


def get_unlocked_badge_count():
    count = 0

    for badge in get_badges():
        if badge[1]:
            count += 1

    return count


def format_goal(hours):
    if hours == int(hours):
        return str(int(hours)) + " Hours"

    return str(round(hours, 1)) + " Hours"


def format_hours(minutes):
    hours = minutes / 60

    if minutes == 0:
        return "0 hrs"
    elif minutes % 60 == 0:
        return str(int(hours)) + " hrs"

    return str(round(hours, 1)) + " hrs"


def format_duration(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours == 0:
        return str(remaining_minutes) + " min"
    elif remaining_minutes == 0:
        return str(hours) + " hr"

    return str(hours) + " hr " + str(remaining_minutes) + " min"


def get_button_action(x, y):
    for button in buttons:
        if button["x1"] <= x <= button["x2"] and button["y1"] <= y <= button["y2"]:
            return button["action"]

    return None


def get_click(canvas):
    click = canvas.wait_for_click()

    try:
        return click.x, click.y
    except:
        return canvas.get_mouse_x(), canvas.get_mouse_y()


def draw_rect(canvas, x1, y1, x2, y2, color):
    try:
        canvas.create_rectangle(x1, y1, x2, y2, color)
    except:
        shape = canvas.create_rectangle(x1, y1, x2, y2)
        canvas.set_color(shape, color)


def draw_text(canvas, x, y, text, size, color):
    try:
        canvas.create_text(x, y, text=text, font_size=size, color=color)
    except:
        canvas.create_text(x, y, text)


if __name__ == "__main__":
    main()
