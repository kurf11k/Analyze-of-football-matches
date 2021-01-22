import csv
from datetime import datetime
import statistics
import math

path = "season-1617_csv.csv"
count_last_matches = 5

date_col = 1
home_team_col = 2
away_team_col = 3
home_fulltime_goals_col = 4
away_fulltime_goals_col = 5
result_fulltime_col = 6
home_halftime_goals_col = 7
away_halftime_goals_col = 8
result_halftime_col = 9

referee_col = 10

home_shots_col = 11
away_shots_col = 12
home_shots_on_target_col = 13
away_shots_on_taget_col = 14


home_bet365 = 23
draw_bet365 = 24
away_bet365 = 25


headers = ["Date", "Home", "Away", "Home goals", "Away goals",
           "Result", "Home mean", "Away mean", "Home median", "Away median", "Home Form", "Away Form"]
teams = dict()


def load_rows_from_csv(path):
    rows = []
    with open(file=path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                headers = row
                line_count += 1
            else:
                row[date_col] = date_time_obj = datetime.strptime(
                    row[date_col], '%d/%m/%y')
                row[home_fulltime_goals_col] = int(
                    row[home_fulltime_goals_col])
                row[away_fulltime_goals_col] = int(
                    row[away_fulltime_goals_col])
                rows.append(row)

        return rows


def create_team(team):
    teams[team] = dict()
    teams[team]["name"] = team
    teams[team]["count_matches"] = 0
    teams[team]["matches"] = []

    teams[team]["home"] = dict()
    teams[team]["home"]["matches"] = []
    teams[team]["home"]["count_matches"] = 0
    teams[team]["home"]["scored_goals"] = []
    teams[team]["home"]["conceded_goals"] = []
    teams[team]["home"]["form"] = []

    teams[team]["away"] = dict()
    teams[team]["away"]["matches"] = []
    teams[team]["away"]["count_matches"] = 0
    teams[team]["away"]["scored_goals"] = []
    teams[team]["away"]["conceded_goals"] = []
    teams[team]["away"]["form"] = []


matches = load_rows_from_csv(path)


def sort_by(elem):
    return elem[1]


matches.sort(key=sort_by)

matches_with_props = []


def get_result(diff_size, home_stat, away_stat):
    diff_stat = abs(home_stat - away_stat)

    if(home_stat > away_stat):
        if(diff_stat > diff_size):
            return 1

    elif away_stat > home_stat:
        if diff_stat > diff_size:
            return -1

    return 0


balance = 0
bet_start = 10
bet_actual = bet_start

bet_max = 0
round_bet = 0
count_bets = 0

for match in matches:
    if not match[home_team_col] in teams:
        create_team(match[home_team_col])

    if not match[away_team_col] in teams:
        create_team(match[away_team_col])

    home = teams[match[home_team_col]]
    away = teams[match[away_team_col]]

    if home["home"]["count_matches"] >= count_last_matches and away["away"]["count_matches"] >= count_last_matches:
        home_avg_scored_goals = statistics.mean(home["home"]["scored_goals"]) * statistics.mean(
            away["away"]["conceded_goals"])

        home_median_scored_goals = statistics.median(
            home["home"]["scored_goals"]) * statistics.median(
            away["away"]["conceded_goals"])

        home_form = sum(home["home"]["form"])

        away_avg_scored_goals = statistics.mean(away["away"]["scored_goals"]) * statistics.mean(
            home["home"]["conceded_goals"])

        away_median_scored_goals = statistics.median(
            away["away"]["scored_goals"]) * statistics.median(
            home["home"]["conceded_goals"])

        away_form = sum(away["away"]["form"])

        home["home"]["form"].pop(0)
        away["away"]["form"].pop(0)

        count_goals = 10
        home_prob_of_goals = []
        away_prob_of_goals = []

        for x in range(0, count_goals):
            home_prob_of_goals.append((math.pow(
                home_avg_scored_goals, x) * math.pow(math.e, -home_avg_scored_goals))/math.factorial(x))
            away_prob_of_goals.append((math.pow(
                away_avg_scored_goals, x) * math.pow(math.e, -away_avg_scored_goals))/math.factorial(x))

        tip = 0

        # * forma
        diff_form_size = 3
        tip += get_result(diff_form_size, home_form, away_form)

        # * průměrný počet gólů
        diff_avg_goals_size = 1
        tip += get_result(diff_avg_goals_size,
                          home_avg_scored_goals, away_avg_scored_goals)

        # * medián počtu gólů
        diff_median_goals_size = 1
        #tip += get_result(diff_median_goals_size, home_median_scored_goals, away_median_scored_goals)

        if tip > 0:
            tip = "H"
            odd = float(match[home_bet365])
        elif tip < 0:
            tip = "A"
            odd = float(match[away_bet365])
        else:
            tip = "D"
            odd = float(match[draw_bet365])

        if tip == match[result_fulltime_col] and tip == "D":
            result = "win"
            balance += bet_actual * (odd - 1)
            bet_actual = bet_start
            round_bet = 0
        elif tip == "D":
            result = "loss"
            balance -= bet_actual
            bet_actual = bet_actual * 2
            count_bets += 1
            round_bet += 1
            if bet_actual > bet_max:
                bet_max = bet_actual
        else:
            result = "not bet"

        matches_with_props.append([
            match[date_col].strftime("%d/%m/%y"),
            match[home_team_col], match[away_team_col],
            match[home_fulltime_goals_col],
            match[away_fulltime_goals_col],
            match[result_fulltime_col],
            str(home_avg_scored_goals).replace(".", ","),
            str(away_avg_scored_goals).replace(".", ","),
            str(home_median_scored_goals).replace(".", ","),
            str(away_median_scored_goals).replace(".", ","),
            home_form,
            away_form,
            tip,
            result

        ])

    home["home"]["count_matches"] += 1
    home["home"]["scored_goals"].append(match[home_fulltime_goals_col])
    home["home"]["conceded_goals"].append(match[away_fulltime_goals_col])

    away["away"]["count_matches"] += 1
    home["away"]["scored_goals"].append(match[away_fulltime_goals_col])
    home["away"]["conceded_goals"].append(match[home_fulltime_goals_col])

    if match[result_fulltime_col] == "H":
        home["home"]["form"].append(1)
        away["away"]["form"].append(-1)

    elif match[result_fulltime_col] == "D":
        home["home"]["form"].append(0)
        away["away"]["form"].append(0)

    elif match[result_fulltime_col] == "A":
        home["home"]["form"].append(-1)
        away["away"]["form"].append(1)


with open("season_with_props.csv", "w", newline="") as file:
    csv_writer = csv.writer(file, delimiter=";")
    csv_writer.writerow(headers)
    for match in matches_with_props:
        # print(match)
        csv_writer.writerow(match)

print("Start bet: " + str(bet_start))
print("Max bet: " + str(bet_max))
print("Profit: " + str(balance))
print("Count bets: " + str(count_bets))
