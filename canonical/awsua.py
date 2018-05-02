import boto3
import os
from subprocess import check_call
import time
import urllib


def main():
    if not os.path.exists(os.path.join(os.environ['HOME'], '.aws', 'credentials')):
        check_call(['aws', 'configure'])
    access_key, secret = create_user()
    create_role(access_key, secret)
    delete_access_key(access_key)
    current_account_id = boto3.resource('iam').CurrentUser().user_id
    print("Use Account ID %s when registering" % (current_account_id))


def delete_access_key(access_key):
    iam = boto3.client('iam')
    iam.delete_access_key(UserName='ubuntu-advantage', AccessKeyId=access_key)


def create_user():
    iam = boto3.client('iam')
    users = set(u.get('UserName') for u in iam.list_users().get('Users', []))
    if 'ubuntu-advantage' not in users:
        print("creating user 'ubuntu-advantage'")
        iam.create_user(UserName='ubuntu-advantage')
        print("user 'ubuntu-advantage' created")
    policies = set(p.get('PolicyArn') for p in iam.list_attached_user_policies(
        UserName='ubuntu-advantage').get('AttachedPolicies', []))
    if 'arn:aws:iam::aws:policy/IAMFullAccess' not in policies:
        print("attaching IAM full access policy to user...")
        iam.attach_user_policy(UserName='ubuntu-advantage',
            PolicyArn='arn:aws:iam::aws:policy/IAMFullAccess')
        print("IAM full access policy attached")
    resp = iam.create_access_key(UserName='ubuntu-advantage')
    return resp['AccessKey']['AccessKeyId'], resp['AccessKey']['SecretAccessKey']
 

def create_role(access_key, secret):
    iam = boto3.client('iam',
        aws_access_key_id=access_key, aws_secret_access_key=secret,
    )
    for i in range(45):
        try:
            iam.list_roles()
        except:
            time.sleep(i)
    roles = [r for r in iam.list_roles().get('Roles', []) if r['RoleName'] == 'ubuntu-advantage']
    role = roles and roles.pop() or None
    if not role:
        print("creating role 'ubuntu-advantage'...")
        iam.create_role(
            Path='/',
            RoleName='ubuntu-advantage',
            AssumeRolePolicyDocument="""{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"AWS": "arn:aws:iam::099720109477:root"}, "Action": "sts:AssumeRole", "Condition": {"StringEquals": {"sts:ExternalId": "633a7cb0-4d3f-11e8-9e00-fa163e7bdd5c"}}}]}""",
        )
        print("role 'ubuntu-advantage' created")
    policies = set(p.get('PolicyArn') for p in iam.list_attached_role_policies(
        RoleName='ubuntu-advantage').get('AttachedPolicies', []))
    if 'arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess' not in policies:
        print("attaching read-only policy to role...")
        iam.attach_role_policy(RoleName='ubuntu-advantage', PolicyArn='arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess')
        print("read-only policy attached")
    print("ubuntu-advantage role/policy setup complete")
