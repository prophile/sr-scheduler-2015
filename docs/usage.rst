Usage
=====

The scheduler is run using the ``sr-comp-schedule`` binary.

.. argparse::
    :module: sr.comp.scheduler.args
    :func: argument_parser
    :prog: sr-comp-schedule

The scheduler outputs a match schedule in YAML format, which is suitable
for writing into ``schedule.yaml`` in a compstate repository.

