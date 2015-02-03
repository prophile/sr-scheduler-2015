Algorithm
=========

The SR league scheduling problem can be stated as this:

Given a number of potential match periods [#src]_, a number of arenas and
corners per arena, and a list of teams, find a schedule for the league
matches such that:

 * No team is required to be in more than one place at once (*consistency*),
 * All teams have the same number of matches (*equality*),
 * The matches of any particular are spaced by at least *s* matches for some
   *s* (*spacing*),
 * Each team faces another team a maximum of *r* times (*wide competition*),
 * A maximum of one corner is left unoccupied in each match (*occupancy*),
 * Teams' matches have an even distribution of start zones (*zone
   distribution*).

Rounds
------

The approach used in recent years has been to partition matches into
*rounds*. A round is a contiguous block of match periods in which each team
appears exactly once. By using a round structure the *consistency* and
*equality* constraints are satisfied by construction. Within each round the
*spacing* constraint is also implied, and thus only needs to be checked on
the interfaces between rounds.

``match-scheduler2``
--------------------

For the 2013 competition, Alistair Lynn wrote a scheduler under the name
``match-scheduler2``. This scheduler assigned a weight based on a schedule's
"badness" and then performed hill-climbing from an initial random schedule
to improve it to an acceptable level. Since most of the constraints were
hard constraints, this proved to be a mistake. After having to manually
tweak the generated schedule for 2013, Peter Law and Sam Phippen developed a
system called ``blueflame`` which made a number of peephole improvements to
generated schedules.

``SMT``
-------

Jeremy Morse, who had worked with such things before, made an observation
before the 2014 competition that considered as hard constraints, the match
scheduling problem could be reduced to SAT. Using the z3 SMT solver, a
scheduler was written which produced a roundwise schedule enforcing
between-round *separation* with SMT constraints.

This worked, but had two pitfalls:

 1. Being SAT, it was very slow;
 2. It could not solve for the *wide competition* constraint and required
    manual work after finishing for that and the *zone distribution*
    constraint.

The Algorithm
-------------

The general idea behind this scheduler is to:

 1. Greedily generate a round at a time,
 2. Schedule the next round from a random permutation of matches until one
    is found that satisfies all constraints,
 3. Ensure zone distribution in a post-processing pass.

The list of teams is padded out with "pseudo-teams": sentinels that stand in
for empty spaces in a match. In the inner loop of the scheduler, the team
list is randomly permuted, partitioned into match periods, and then run
against a validator with previous matches.

The validator validates the *spacing*, *wide competition* and *occupancy*
constraints.

After enough random permutations have been tried, the algorithm may give up
and backtrack one round.

Once all match periods have been scheduled, the appearances in each match
are also randomly permuted. This ensures a statistically even distribution
of zones, in accordance with the *zone distribution* constraint.

Partial Rescheduling
--------------------

In certain circumstances (notably, if significant numbers of teams have
dropped out over the course of the competition) it may be beneficial to run
a partial reschedule—to provide a schedule using a number of matches from
the previous schedule. This is supported by seeding matches in the greedy
algorithm and continuing scheduling from there.

.. warning:: If the schedule up to the point where the scheduler is started
   is invalid, the scheduler will never terminate.

.. [#src] In this case calculated from the match period length and the day
   schedule in a ``schedule.yaml`` from a compstate repository.

