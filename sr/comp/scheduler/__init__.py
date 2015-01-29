__all__ = ['scheduler', 'metadata']

try:
    from .scheduler import Scheduler, max_possible_match_periods, main
except ImportError:
    pass

