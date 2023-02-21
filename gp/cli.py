import multiprocessing
from collections import defaultdict

import click
import tabulate

from gp.event import Event, EventType
from gp.game import Game
from gp.logger import EventLogger
from gp.players import BOT_TYPES, Human
from gp.players.stats import WithStats
from gp.runner import GameRunner
from gp.tournament import Tournament


GAME_LOG = "game.log"


@click.group()
@click.option(
    "--game-log",
    type=click.Path(exists=False, writable=True, file_okay=True, dir_okay=False),
    default=None,
)
@click.pass_context
def main(ctx, game_log):
    ctx.obj = {"callbacks": []}
    if game_log:
        log_file = open(game_log, "a")
        event_logger = EventLogger(log_file)
        ctx.obj["callbacks"].append(EventType.ANY, event_logger)


def announce_winner(event: Event):
    print(f"{event.data['winner'].name()} won!")


@main.command()
@click.pass_context
def play(ctx):
    runner = GameRunner()
    for t, c in ctx.obj["callbacks"]:
        runner.register_callback(t, c)
    runner.register_callback(EventType.GAME_END, announce_winner)

    p1_name = input("Player 1 name: ")
    p2_name = input("Player 2 name: ")
    game = Game([Human(0, p1_name), Human(1, p2_name)])
    runner.run(game)


def mean(xs):
    return sum(xs) / len(xs)


HTML_STYLE = """
table {
	border-collapse: collapse;
    font-family: Tahoma, Geneva, sans-serif;
    text-align: center;
}
table tr td {
	padding: 0px;
    background-color: #ddd;
}
td div {
    padding: 15px;
}
table thead th, table tr td:nth-child(1) {
	background-color: #54585d;
	color: #ffffff;
	font-weight: bold;
	font-size: 13px;
	border: 1px solid #54585d;
    padding: 15px;
}
table tbody td {
	color: #000;
	border: 1px solid #dddfe1;
}
.darkgreen {
    background-color: #0b0;
}
.lightgreen {
    background-color: #0f0;
}
.darkred {
    background-color: #b00;
}
.lightred {
    background-color: #f00;
}
.grey {
    background-color: #ddd;
}
"""


HTML_TEMPLATE = """
<html>
<head><style>{style}</style></head>
<body>{body}</body>
</html>
"""


def color(score):
    # if score >= 80.0:
    #     color = "lightgreen"
    if score > 50.0:
        color = "darkgreen"
    # elif score <= 20.0:
    #     color = "lightred"
    elif score < 50.0:
        color = "darkred"
    else:
        color = "grey"
    return f'<div class="{color}">{score:.1f}</div>'


@main.command()
@click.argument("bot", nargs=-1)
@click.option("--matches", "-m", type=int, default=100)
@click.option("--html", type=click.Path(dir_okay=False))
@click.option("--workers", "-w", type=int, default=multiprocessing.cpu_count())
@click.pass_context
def bot_duels(ctx, bot, matches, html, workers):
    if bot == ():
        bot_types = list(BOT_TYPES.items())
    else:
        bot_types = [(b, BOT_TYPES[b]) for b in bot]

    scores = defaultdict(dict)
    n = len(bot_types) * (len(bot_types) - 1) // 2
    c = 1
    for i, (n1, t1) in enumerate(bot_types):
        for n2, t2 in bot_types[i + 1 :]:
            print(f"{c}/{n}", end="\r")
            c += 1
            tourney = Tournament(
                matches, [t1(0, n1), t2(1, n2)], ctx.obj["callbacks"], workers=workers
            )
            tourney.run()
            scores[n1][n2] = 100.0 * tourney.scores[n1] / matches
            scores[n2][n1] = 100.0 * tourney.scores[n2] / matches

    mean_scores = sorted(
        [(name, round(mean(scores.values()), 2)) for name, scores in scores.items()],
        key=lambda t: t[1],
        reverse=True,
    )

    headers = ["Player", "Mean"] + [t[0] for t in mean_scores]

    rows = [headers]
    for name, mean_score in mean_scores:
        print(f"{name}: {mean_score}")

        row = [name, color(mean_score)]
        for opponent, _ in mean_scores:
            if name == opponent:
                row.append("-")
            else:
                row.append(color(scores[name][opponent]))

        rows.append(row)

    if html:
        with open(html, "w") as f:
            table = tabulate.tabulate(rows, headers="firstrow", tablefmt="unsafehtml")
            f.write(HTML_TEMPLATE.format(body=table, style=HTML_STYLE))


@main.command()
@click.argument("bot", nargs=-1)
@click.option("--matches", "-m", type=int, default=100)
@click.pass_context
def bot_battle_royale(ctx, bot, matches):
    if bot == ():
        bot_types = list(BOT_TYPES.items())
    else:
        bot_types = [(b, BOT_TYPES[b]) for b in bot]

    bots = [WithStats(t, i, n) for i, (n, t) in enumerate(bot_types)]
    tourney = Tournament(matches, bots, ctx.obj["callbacks"])
    tourney.run()

    wins = sorted(zip(bots, tourney.scores), key=lambda t: t[1], reverse=True)
    for bot, w in wins:
        print(f"{bot.name()}: {w}")


if __name__ == "__main__":
    main()
