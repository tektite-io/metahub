import boto3
from botocore.exceptions import BotoCoreError, ClientError

from AwsHelpers import assume_role, get_boto3_session

def run_metatags(logger, finding, mh_filters_tags, mh_role):
    """
    Executes Tags discover for the AWS Resource Type
    :param logger: logger configuration
    :param finding: AWS Security Hub finding complete
    :param mh_filters: MetaHub filters (--mh-filters-tags)
    :param mh_role: AWS IAM Role to be assumed in the AWS Account (--mh-role)
    :return: mh_tags_values (the MetaTags output as dictionary), mh_tags_matched (a Boolean to confirm if the resource matched the filters)
    """

    # Get a Boto3 Session in the Child Account if mh_role is passed
    AwsAccountId = finding["AwsAccountId"]
    if mh_role:
        sh_role_assumend = assume_role(logger, AwsAccountId, mh_role)
        sess = get_boto3_session(sh_role_assumend)
        logger.info(
            "Assuming IAM Role: %s (%s)",
            mh_role,
            AwsAccountId,
        )
    else:
        sess = None

    AWSResourceType = finding["Resources"][0]["Type"]
    AWSResourceId = finding["Resources"][0]["Id"]

    if not sess:
        client = boto3.client('resourcegroupstaggingapi')
    else:
        client = sess.client(service_name="resourcegroupstaggingapi")

    tags = False
    try:
        response = client.get_resources(
            ResourceARNList=[
                AWSResourceId,
            ]
        )
        try:
            tags = response['ResourceTagMappingList'][0]['Tags']
        except IndexError:
            logger.error("No Tags found for resource: %s", AWSResourceId)
    except ClientError as err:
        logger.error("Error Fetching Tags: %s", err)

    mh_tags_values = {}
    mh_tags_matched = False if mh_filters_tags else True

    if tags:
        for tag in tags:
            mh_tags_values.update({tag["Key"]: tag["Value"]})
        compare = {k: mh_tags_values[k] for k in mh_tags_values if k in mh_filters_tags and mh_tags_values[k] == mh_filters_tags[k]}
        logger.info(
            "Evaluating MetaTag filter. Expected: "
            + str(mh_filters_tags)
            + " Found: "
            + str(bool(compare))
        )
        if mh_filters_tags and bool(compare):
            mh_tags_matched = True

    return mh_tags_values, mh_tags_matched