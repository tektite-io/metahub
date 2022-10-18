import argparse
import logging

class KeyValueWithList(argparse.Action):
    """Parser keyvalue with list Action"""

    def __call__(self, parser, namespace, values, option_string=None):
        #setattr(namespace, self.dest, dict())
        setattr(namespace, self.dest, Dictlist())
        logger = get_logger("ERROR")
        for value in values:
            # split it into key and value
            try:
                key, value = value.split("=")
            except ValueError:
                logger.error("ERROR: Incorrect Key=Value format: " + value)
                exit(1)
            # Dictionary:
            getattr(namespace, self.dest)[key] = value

class KeyValue(argparse.Action):
    """Parser keyvalue Action"""

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        logger = get_logger("ERROR")
        for value in values:
            # split it into key and value
            try:
                key, value = value.split("=")
            except ValueError:
                logger.error("ERROR: Incorrect Key=Value format: " + value)
                exit(1)
            # Dictionary:
            getattr(namespace, self.dest)[key] = value

class Dictlist(dict):
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)

    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)


def get_parser():
    """Configure Parser"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
    MetaHub for AWS Security Hub
    """,
    )
    parser.add_argument(
        "--list-findings",
        help="Use this option to list Security Hub findings (based on filters)",
        required=False,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--sh-filters",
        default=None,
        help='Security Hub Filters: Use this option to filter the result from Security Hub. \
            Set a number of key-value pairs (do not put spaces before or after the = sign). \
            If a value contains spaces, you should define it with double quotes: Filter="This is a value  \
            Example: ./metahub --list-findings --sh-filters ResourceType=AwsEc2SecurityGroup\
            Default: RecordState=ACTIVE WorkflowStatus=NEW ProductName="Security Hub"',
        required=False,
        nargs="*",
        action=KeyValueWithList,
    )
    parser.add_argument(
        "--list-metachecks",
        help="Use this option to list all available Meta Checks",
        required=False,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--meta-checks",
        help="Use this option to enable Meta Checks",
        required=False,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--mh-filters",
        default=None,
        help="MetaHub Filters: Use this option to filter the resources based on Meta Checks results. \
            You can list available Meta Checks using --list-metachecks \
            Set a number of key-value pairs (do not put spaces before or after the = sign). \
            Only True or False valid values. \
            Example: ./metahub --list-findings  --meta-checks --mh-filters is_attached_to_ec2_instance_with_public_ip=True is_public=False \
            Default: None",
        required=False,
        nargs="*",
        action=KeyValue,
    )
    parser.add_argument(
        "--update-findings",
        default=None,
        help='Security Hub Update Fields: Use this option to update your findings. You need to speficy wich field to update and with wich value. \
            Set a number of key-value pairs (do not put spaces before or after the = sign). \
            If a value contains spaces, you should define it with double quotes: Key="This is a value  \
            Example: ./metahub --list-findings --update-findings Workflow=RESOLVED \
            Default: None',
        required=False,
        nargs="*",
        action=KeyValue,
    )
    parser.add_argument(
        "--sh-assume-role",
        default=None,
        help="The AWS IAM role name to be assumed where SH is running. \
        Needs to be uses with --sh-account.",
        required=False,
    )
    parser.add_argument(
        "--sh-account",
        default=None,
        help="The AWS Account ID where your SH is running. \
        Needs to be uses with --sh-assume-role.",
        required=False,
    )
    parser.add_argument(
        "--mh-assume-role",
        default=None,
        help="The AWS IAM role name to be assumed where resources ares running.",
        required=False,
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output. Default is full. Options: short, json, inventory, statistics",
        required=False,
    )
    parser.add_argument(
        "--log-level",
        default="ERROR",
        help="Log Level (Default: ERROR) (Valid Options: ERROR, WARNING, INFO or DEBUG)",
        required=False,
    )
    return parser

def get_logger(log_level):
    """Configure Logger"""
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    if log_level in ("INFO" "ERROR" "WARNING" "DEBUG"):
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(process)d - %(filename)s:%(funcName)s - [%(levelname)s] %(message)s",
        )
        return logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(process)d - %(filename)s:%(funcName)s - [%(levelname)s] %(message)s",
    )
    logger.info("--log-level incorrect value, using DEBUG...")
    return logger

color = {
    "PURPLE": "\033[95m",
    "CYAN": "\033[96m",
    "DARKCYAN": "\033[36m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
    "END": "\033[0m",
    "CRITICAL": "\033[91m",
    "HIGH": "\033[91m",
    "MEDIUM": "\033[93m",
    "LOW": "\033[94m",
}