import argparse
import logging
import sys
import os
import re
import glob
import json

_logger = logging.getLogger(__name__)
__version__ = "0.0.1"
__no_fields__ = 10
__TIMESTAMP__ = 0
__IP__ = 2
__RESP_HEADER__ = 1
__RESP_SIZE__ = 4

class FileStats():
    """Stores computations for a log file.
    """
    def __init__(self) -> None:
        self.file = ""
        self.ip = {}
        self.eps = 0
        self.tbe = 0

def process_file(args, file_name):
    '''Processes an individual file
    '''
    stats = FileStats()
    stats.file = file_name
    with open(file_name, "r") as f:
        line_count = 0
        f.readline()
        while True:
            try:
                line = f.readline()
                if not line:
                    break
                line = re.sub(r'\s+', r' ', line)
                fields = line.strip().split(' ')
                timestamp = fields[__TIMESTAMP__]
                if line_count == 0:
                    start_time = timestamp
                if len(fields)<__no_fields__:
                    _logger.error(f"Line {line_count} for file {file_name} has not enough fields. Skipping.")
                    line_count += 1
                    continue
                if args.mfip or args.lfip:
                    ip=fields[__IP__]
                    if ip in stats.ip:
                        stats.ip[ip]+=1
                    else:
                        stats.ip[ip]=1
                if args.tbe:
                    try:
                        ex0 = fields[__RESP_HEADER__]
                        ex1 = fields[__RESP_SIZE__]
                        be=int(ex0)+int(ex1)
                        stats.tbe+=be
                    except ValueError:
                        _logger.error(f"Bad values {ex0} {ex1} for bytes exchanged in line {line_count} for file {file_name}. Skipping.")
                        line_count += 1
                        continue
                line_count += 1
            except UnicodeDecodeError:
                _logger.error(f"Line {line_count} has incorrect encoding for file {file_name}. Skipping.")
                line_count += 1
        _logger.info(f'Processed file {file_name} for {line_count} lines.')
    end_time = timestamp
    if float(start_time) > float(end_time):
            _logger.error(f"End time is former to Start Time. File {file_name} is corrupted.")
    stats.eps = line_count/(float(end_time) - float(start_time))
    return stats

def process(args):
    """Log Processing of all files.

    Args:
      args (ArgumentParser)
    """
    global_stats = []
    for file_name in args.filenames:
        if os.path.isdir(file_name):
            for file in glob.glob(os.path.join(file_name ,'*.log')):
                stats = process_file(args, file)
                global_stats.append(stats)
        else:
            stats = process_file(args, file_name)
            global_stats.append(stats)
            
    all_files=[]
    for stats in global_stats:
        if args.mfip:
            mfip = min(stats.ip)
        else:
            mfip = None
        if args.lfip:
            lfip = max(stats.ip)
        else:
            lfip = None
        if args.tbe:
            tbe = stats.tbe
        else:
            tbe = None
        if args.eps:
            eps = stats.eps
        else:
            eps = None
        serializable = {"File":os.path.basename(stats.file),
                        "MostFrequentIP":mfip,
                        "LeastFrequentIP":lfip,
                        "EventsPerSecond":eps,
                        "TotalAmountsBytesExchanged":tbe}
        all_files.append(serializable)
    data = json.dumps(all_files)
    with open(args.output, "w") as outfile:
        outfile.write(data)
            
def parse_args(args):
    """Parse command line parameters
    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Log Processor")
    parser.add_argument(
        "--version",
        action="version",
        version="Assignment {ver}".format(ver=__version__),
    )
    parser.add_argument('filenames', nargs='+')
    parser.add_argument(
        "-m",
        "--most_frequent_ip",
        dest="mfip",
        help="Computes most frequent IP",
        action="store_true"
    )
    parser.add_argument(
        "-l",
        "--least_frequent_ip",
        dest="lfip",
        help="Computes least frequent IP",
        action="store_true"
    )
    parser.add_argument(
        "-e",
        "--events_per_second",
        dest="eps",
        help="Computes events per second",
        action="store_true"
    )
    parser.add_argument(
        "-t",
        "--total_bytes_exchanged",
        dest="tbe",
        help="Computes total bytes exchanged",
        action="store_true"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """
    Entrypoint.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting Log Processing")
    try:
        process(args)
    except Exception as e:
        _logger.info(f"Unknown exception {e}")
    _logger.info("Ended Log Processing")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`"""
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
