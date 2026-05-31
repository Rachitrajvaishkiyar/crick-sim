import datetime
import random
from itertools import combinations



class Person:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def __repr__(self):
        return f"{self.name} ({self.role})"


class Team:
    def __init__(self, name, country):
        self.name = name
        self.country = country
        self.members = []

        self.group = None
        self.matches_played = 0
        self.wins = 0
        self.losses = 0
        self.points = 0

        self.runs_scored = 0
        self.overs_faced = 0
        self.runs_conceded = 0
        self.overs_bowled = 0

    def add_member(self, person):
        self.members.append(person)

    def reset_stats(self):
        self.matches_played = 0
        self.wins = 0
        self.losses = 0
        self.points = 0
        self.runs_scored = 0
        self.overs_faced = 0
        self.runs_conceded = 0
        self.overs_bowled = 0

    @property
    def nrr(self):
        if self.overs_faced == 0 or self.overs_bowled == 0:
            return 0.0
        return round(
            (self.runs_scored / self.overs_faced) -
            (self.runs_conceded / self.overs_bowled),
            3
        )

    def __repr__(self):
        return self.name


class Match:
    def __init__(self, team_a, team_b, group):
        self.team_a = team_a
        self.team_b = team_b
        self.group = group
        self.winner = None
        self.date = datetime.date.today()

    def play(self):
        overs = 20
    
        runs_a = random.randint(120, 220)
        runs_b = random.randint(120, 220)
    
        self.team_a.runs_scored += runs_a
        self.team_a.runs_conceded += runs_b
        self.team_a.overs_faced += overs
        self.team_a.overs_bowled += overs
    
        self.team_b.runs_scored += runs_b
        self.team_b.runs_conceded += runs_a
        self.team_b.overs_faced += overs
        self.team_b.overs_bowled += overs
    
        if runs_a > runs_b:
            self.winner = self.team_a
            loser = self.team_b
        else:
            self.winner = self.team_b
            loser = self.team_a
    
        self.winner.points += 2
        self.winner.wins += 1
        self.winner.matches_played += 1
    
        loser.losses += 1
        loser.matches_played += 1
    
        return self.winner.name



class TournamentSystem:
    def __init__(self):
        self.teams = []
        self.quarterfinals = []
        self.semifinals = []
        self.final = None
        self.champion = None
        self.groups = {"A": [], "B": [], "C": [], "D": []}
        self.matches = []
        self.stage = "INIT"  # INIT → GROUPS → MATCHES → PLAYED


    def generate_knockouts(self):
        if self.stage != "PLAYED":
            raise RuntimeError("Complete group stage first")

        qualified = self.get_qualified_teams()

        A1, A2 = qualified[0], qualified[1]
        B1, B2 = qualified[2], qualified[3]
        C1, C2 = qualified[4], qualified[5]
        D1, D2 = qualified[6], qualified[7]

        self.quarterfinals = [
            Match(A1, B2, "QF"),
            Match(B1, A2, "QF"),
            Match(C1, D2, "QF"),
            Match(D1, C2, "QF"),
        ]

        self.stage = "QF"

    def play_quarterfinals(self):
        winners = []
        for match in self.quarterfinals:
            match.play()
            winners.append(match.winner)

        self.semifinals = [
            Match(winners[0], winners[2], "SF"),
            Match(winners[1], winners[3], "SF"),
        ]

        self.stage = "SF"
        return winners
    
    def play_semifinals(self):
        winners = []
        for match in self.semifinals:
            match.play()
            winners.append(match.winner)
    
        self.final = Match(winners[0], winners[1], "FINAL")
        self.stage = "FINAL"
        return winners
    
    def play_final(self):
        if self.stage != "FINAL":
            raise RuntimeError("Final not ready")
    
        self.final.play()
        self.champion = self.final.winner
        self.stage = "COMPLETED"
        return self.champion

    def load_fixed_teams(self):
        team_names = [
            "India",
            "Australia",
            "England",
            "South Africa",
            "New Zealand",
            "Pakistan",
            "West Indies",
            "Sri Lanka",
            "Afghanistan",
            "Bangladesh",
            "Netherlands",
            "Zimbabwe",
            "Ireland",
            "Scotland",
            "Namibia",
            "USA",
        ]

        self.teams.clear()
        for name in team_names:
            team = Team(name, name)
            team.add_member(Person("Captain", "Player"))
            team.add_member(Person("Coach", "Staff"))
            self.teams.append(team)

        self.stage = "INIT"


    def generate_groups(self):
        if len(self.teams) != 16:
            raise ValueError("Exactly 16 teams required")

        random.shuffle(self.teams)
        for i, group in enumerate(self.groups.keys()):
            self.groups[group] = self.teams[i * 4 : (i + 1) * 4]
            for team in self.groups[group]:
                team.group = group
                team.reset_stats()

        self.matches.clear()
        self.stage = "GROUPS"

    def get_groups(self):
        return self.groups


    def generate_matches(self):
        if self.stage != "GROUPS":
            raise RuntimeError("Generate groups first")

        self.matches.clear()
        for group, teams in self.groups.items():
            for t1, t2 in combinations(teams, 2):
                self.matches.append(Match(t1, t2, group))

        self.stage = "MATCHES"

    def get_matches(self):
        return self.matches


    def play_all_matches(self):
        if self.stage != "MATCHES":
            raise RuntimeError("Generate matches first")

        results = []
        for match in self.matches:
            winner = match.play()
            results.append(
                {
                    "group": match.group,
                    "team_a": match.team_a.name,
                    "team_b": match.team_b.name,
                    "winner": winner,
                }
            )

        self.stage = "PLAYED"
        return results


    def get_group_standings(self):
        standings = {}
    
        for group, teams in self.groups.items():
            standings[group] = sorted(
                teams,
                key=lambda t: (t.points, t.nrr),
                reverse=True
            )
    
        return standings


    def get_qualified_teams(self):
        qualified = []
        standings = self.get_group_standings()

        for group in standings:
            qualified.extend(standings[group][:2])

        return qualified
