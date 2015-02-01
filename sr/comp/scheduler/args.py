from .metadata import DESCRIPTION, VERSION
import argparse

def argument_parser():
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
    parser.add_argument('-a', '--appearances-per-round',
                        type=int,
                        default=1,
                        help='number of times each team appears in each round')
    parser.add_argument('--lcg',
                        action='store_true',
                        dest='lcg',
                        help='enable LCG permutation')
    parser.add_argument('--parallel',
                        type=int,
                        default=1,
                        help='number of parallel threads')
    parser.add_argument('-v', '--version',
                        action='version',
                        version=VERSION,
                        help='display version and exit')
    return parser

