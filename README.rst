sr.comp.scheduler
=================

This is a competition league schedule generator. When fed a compstate
repo, it will generate all the league match entries for `schedule.yaml`.

Run with ``sr-comp-schedule``.

The general strategy for planning matches is:

#. schedule a round at a time
#. randomly permute the list of teams then partition it into matches each pass through
#. if it fits the criteria, add it then move on to the next round
#. if 1000 permutations pass without a hit, backtrack one round

The criteria are:

* match separation (appearances at least n matches apart)
* facing constraints (can only face any particular other team a maximum of m times)
* at most only one of the slots is empty in any match
