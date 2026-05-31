import tkinter as tk
from tkinter import messagebox, ttk

from backend import TournamentSystem


class TournamentUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cricket Tournament System")
        self.root.geometry("900x600")

        self.app = TournamentSystem()
        self.app.load_fixed_teams()

        self.create_widgets()


    def create_widgets(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        ttk.Button(
            btn_frame, text="Generate Groups", command=self.generate_groups
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text="Generate Matches", command=self.generate_matches
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Play All Matches", command=self.play_matches).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Show Standings", command=self.show_standings).pack(
            side=tk.LEFT, padx=5
        )

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(expand=True, fill=tk.BOTH)

        self.group_tab = ttk.Frame(self.tabs)
        self.match_tab = ttk.Frame(self.tabs)
        self.standings_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.group_tab, text="Groups")
        self.tabs.add(self.match_tab, text="Matches")
        self.tabs.add(self.standings_tab, text="Standings")

        self.create_group_tab()
        self.create_match_tab()
        self.create_standings_tab()
        self.knockout_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.knockout_tab, text="Knockouts")
        self.create_knockout_tab()


    def create_knockout_tab(self):
        btn_frame = tk.Frame(self.knockout_tab)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Generate QFs", command=self.generate_qf).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Play QFs", command=self.play_qf).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Play SFs", command=self.play_sf).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Play Final", command=self.play_final).pack(
            side=tk.LEFT, padx=5
        )

        self.knockout_tree = ttk.Treeview(
            self.knockout_tab,
            columns=("Stage", "Team A", "Team B", "Winner"),
            show="headings",
        )

        for col in ("Stage", "Team A", "Team B", "Winner"):
            self.knockout_tree.heading(col, text=col)

        self.knockout_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def create_group_tab(self):
        self.group_tree = ttk.Treeview(
            self.group_tab, columns=("Group", "Team"), show="headings"
        )
        self.group_tree.heading("Group", text="Group")
        self.group_tree.heading("Team", text="Team")
        self.group_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def generate_groups(self):
        try:
            self.app.generate_groups()
            self.group_tree.delete(*self.group_tree.get_children())

            for group, teams in self.app.get_groups().items():
                for team in teams:
                    self.group_tree.insert("", tk.END, values=(group, team.name))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_match_tab(self):
        self.match_tree = ttk.Treeview(
            self.match_tab,
            columns=("Group", "Team A", "Team B", "Winner"),
            show="headings",
        )

        for col in ("Group", "Team A", "Team B", "Winner"):
            self.match_tree.heading(col, text=col)

        self.match_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def generate_matches(self):
        try:
            self.app.generate_matches()
            self.match_tree.delete(*self.match_tree.get_children())

            for match in self.app.get_matches():
                self.match_tree.insert(
                    "",
                    tk.END,
                    values=(match.group, match.team_a.name, match.team_b.name, ""),
                )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def play_matches(self):
        try:
            results = self.app.play_all_matches()
            self.match_tree.delete(*self.match_tree.get_children())

            for r in results:
                self.match_tree.insert(
                    "",
                    tk.END,
                    values=(r["group"], r["team_a"], r["team_b"], r["winner"]),
                )

        except Exception as e:
            messagebox.showerror("Error", str(e))


    def create_standings_tab(self):
        self.standings_tree = ttk.Treeview(
            self.standings_tab,
            columns=("Group", "Team", "P", "W", "L", "Pts", "NRR"),
            show="headings"
        )
    
        for col in ("Group", "Team", "P", "W", "L", "Pts", "NRR"):
            self.standings_tree.heading(col, text=col)
            self.standings_tree.column(col, anchor="center", width=100)
    
        self.standings_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)


    def show_standings(self):
        self.standings_tree.delete(*self.standings_tree.get_children())

        standings = self.app.get_group_standings()
        for group, teams in standings.items():
            for team in teams:
                self.standings_tree.insert(
                    "",
                    tk.END,
                    values=(
                        group,
                        team.name,
                        team.matches_played,
                        team.wins,
                        team.losses,
                        team.points,
                        team.nrr,
                    ),
                )

    def generate_qf(self):
        self.app.generate_knockouts()
        self.knockout_tree.delete(*self.knockout_tree.get_children())

        for m in self.app.quarterfinals:
            self.knockout_tree.insert(
                "", tk.END, values=("QF", m.team_a.name, m.team_b.name, "")
            )

    def play_qf(self):
        self.app.play_quarterfinals()
        self.refresh_knockouts()

    def play_sf(self):
        self.app.play_semifinals()
        self.refresh_knockouts()

    def play_final(self):
        champion = self.app.play_final()
        self.refresh_knockouts()
        messagebox.showinfo("Champion", f"🏆 Champion: {champion.name}")

    def refresh_knockouts(self):
        self.knockout_tree.delete(*self.knockout_tree.get_children())

        for m in self.app.quarterfinals:
            self.knockout_tree.insert(
                "",
                tk.END,
                values=(
                    "QF",
                    m.team_a.name,
                    m.team_b.name,
                    m.winner.name if m.winner else "",
                ),
            )

        for m in self.app.semifinals:
            self.knockout_tree.insert(
                "",
                tk.END,
                values=(
                    "SF",
                    m.team_a.name,
                    m.team_b.name,
                    m.winner.name if m.winner else "",
                ),
            )

        if self.app.final:
            self.knockout_tree.insert(
                "",
                tk.END,
                values=(
                    "FINAL",
                    self.app.final.team_a.name,
                    self.app.final.team_b.name,
                    self.app.final.winner.name if self.app.final.winner else "",
                ),
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = TournamentUI(root)
    root.mainloop()
