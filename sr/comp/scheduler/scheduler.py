from __future__ import print_function, division

import random
import sys
from collections import Counter
from itertools import product
from math import ceil
import os.path

import argparse
import yaml
from datetime import timedelta

from multiprocessing import Pool
from .metadata import DESCRIPTION, VERSION

class PatienceCounter(object):
    def __init__(self, threshold):
        self.threshold = threshold
        self.level = 0

    def bump(self):
        self.level += 1

    def reset(self):
        self.level = 0

    def reached(self):
        return self.level >= self.threshold

class Scheduler(object):
    def __init__(self,
                 teams,
                 max_match_periods,
                 arenas=('main',),
                 num_corners=4,
                 random=random,
                 separation=2,
                 max_matchups=2):
        self.num_corners = num_corners
        self.random = random
        self.arenas = tuple(arenas)
        self.max_match_periods = max_match_periods
        self._calculate_teams(teams)
        self._calculate_rounds()
        self.separation = separation
        self.max_matchups = max_matchups
        self.tag = ''

    def lprint(self, *args, **kwargs):
        if self.tag:
            print(self.tag, end='', file=sys.stderr)
        print(*args, file=sys.stderr, **kwargs)

    @property
    def entrants_per_match_period(self):
        return len(self.arenas) * self.num_corners

    def _is_pseudo(self, team):
        return team[0] == '~'

    def _calculate_teams(self, base_teams):
        teams = list(base_teams)
        # account for overflow
        overflow = (self.entrants_per_match_period -
                     (len(teams) % self.entrants_per_match_period))
        if overflow < self.entrants_per_match_period:
            for n in range(overflow):
                teams.append('~{}'.format(n))
        self._teams = teams

    @property
    def total_matches(self):
        return self.num_rounds * self.round_length

    def _calculate_rounds(self):
        self.num_rounds = int(self.max_match_periods * self.entrants_per_match_period
                                // len(self._teams))
        self.round_length = len(self._teams) // self.entrants_per_match_period

    def _validate(self, schedule, matchup_max=None, matchup_impatience_bump=lambda: None):
        if matchup_max is None:
            matchup_max = self.max_matchups
        # 3 tests in this function:
        #  (1) validate that teams aren't scheduled too tightly
        #  (2) validate that matchups aren't too frequent
        #  (3) validate that no match has two teams sitting out (or if it is, that it's blank)
        matchups = Counter()
        for match_id, match in enumerate(schedule):
            # Test constraint (1)
            previous_matches = schedule[match_id-self.separation:match_id]
            entrants = set(entrant for entrant in match
                            if not self._is_pseudo(entrant))
            for previous_match in previous_matches:
                previous_entrants = set(entrant for entrant in previous_match
                                         if not self._is_pseudo(entrant))
                if entrants & previous_entrants:
                    return False
            # Update constraint (2)
            for arena_id in range(len(self.arenas)):
                game = match[arena_id*self.num_corners:(arena_id+1)*self.num_corners]
                for a, b in product(game, repeat=2):
                    if a >= b:
                        continue
                    a_pseudo, b_pseudo = self._is_pseudo(a), self._is_pseudo(b)
                    # Check constraint (3) while we're here
                    if (a_pseudo and b_pseudo and
                            not all(self._is_pseudo(x) for x in game)):
                        return False
                    elif not a_pseudo and not b_pseudo:
                        matchups.update([(a, b)])
        # No collisions, determine whether teams face a broad range of other teams
        top_repeated_matchups = max(matchups.values())
        if top_repeated_matchups > self.max_matchups:
            # team faces off against one other team too many times
            matchup_impatience_bump()
            return False
        # No objections, your honour!
        return True

    def run(self):
        matchup_impatience = PatienceCounter(200000)
        max_matchups = self.max_matchups
        matches = []
        teams = list(self._teams)
        while len(matches) < self.total_matches:
            this_round = len(matches) // self.round_length
            self.lprint('Scheduling round {round} ({prev}/{tot} complete)'.format(
                            round=this_round,
                            prev=len(matches),
                            tot=self.total_matches))
            for tick in range(10000):
                if matchup_impatience.reached():
                    matchup_impatience.reset()
                    self.lprint('  Easing off on matchup constraint.')
                    max_matchups += 1
                self.random.shuffle(teams)
                matches_prime = matches + self._match_partition(teams)
                if self._validate(matches_prime, max_matchups, matchup_impatience.bump):
                    matches = matches_prime
                    break
            else:
                self.lprint('  backtracking')
                matches = matches[:-self.round_length]
        return self._clean(matches)

    def _match_partition(self, teams):
        entries = []
        for n in range(0, len(teams), self.entrants_per_match_period):
            entries.append(teams[n:n+self.entrants_per_match_period])
        return entries

    def _clean(self, matches):
        def get_match(match):
            data = {}
            for arena_id, arena in enumerate(self.arenas):
                entrants = match[arena_id*self.num_corners:(arena_id+1)*self.num_corners]
                # Shuffle entrants to get statistically sensible zone distribution
                self.random.shuffle(entrants)
                entrants = [None if self._is_pseudo(entrant) else entrant
                             for entrant in entrants]
                data[arena] = entrants
            return data
        return {match_id: get_match(match) for match_id, match in enumerate(matches)}

def max_possible_match_periods(sched_db):
    # Compute from the contents of a schedule.yaml the number of league periods
    match_period_length = sched_db['match_period_lengths']['total']
    total_league_time = sum((period['end_time'] - period['start_time']
                              for period in sched_db['match_periods']['league']),
                             timedelta())
    return int(total_league_time.total_seconds() // match_period_length)

def main(*args):
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('compstate',
                        type=str,
                        help='competition state git repository')
    parser.add_argument('-s', '--spacing',
                        type=int,
                        default=2,
                        help='number of matches between any two appearances by a team')
    parser.add_argument('-r', '--max-repeated-matchups',
                        type=int,
                        default=2,
                        help='maximum times any team can face any given other team')
    parser.add_argument('--parallel',
                        type=int,
                        default=1,
                        help='number of parallel threads')
    parser.add_argument('-v', '--version',
                        action='version',
                        version=VERSION,
                        help='display version and exit')
    args = parser.parse_args(args)

    with open(os.path.join(args.compstate, 'arenas.yaml')) as f:
        arenas_db = yaml.load(f)
        arenas = arenas_db['arenas'].keys()
        num_corners = len(arenas_db['corners'])

    with open(os.path.join(args.compstate, 'teams.yaml')) as f:
        teams = yaml.load(f)['teams'].keys()

    with open(os.path.join(args.compstate, 'schedule.yaml')) as f:
        sched_db = yaml.load(f)
        max_periods = max_possible_match_periods(sched_db)

    scheduler = Scheduler(teams=teams,
                          max_match_periods=max_periods,
                          arenas=arenas,
                          num_corners=num_corners,
                          separation=args.spacing,
                          max_matchups=args.max_repeated_matchups)
    if args.parallel > 1:
        scheduler.lprint('Using {} threads'.format(args.parallel))
        pool = Pool(args.parallel)
        def get_output(data):
            yaml.dump({'matches': data}, sys.stdout)
            pool.terminate()
        for n in range(args.parallel):
            scheduler.random = random.Random()
            scheduler.tag = '[Thread {}] '.format(n)
            pool.apply_async(scheduler.run,
                             callback=get_output)
        pool.close()
        pool.join()
    else:
        output_data = scheduler.run()
        yaml.dump({'matches': output_data}, sys.stdout)

