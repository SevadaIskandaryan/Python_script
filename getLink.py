import boto3
import json
import argparse


def getDataLink(bucketName, objectName, instanceIDs):

    #getting instances metadata
    client = boto3.client('ec2')
    if instanceIDs[0] == "all":
        response = client.describe_instances()
    else:
        response = client.describe_instances(
                InstanceIds=[
                    *instanceIDs
                ]
        )

    #inserting the response in a json file
    with open('upload.json', 'w') as f:
        listTmp =[]
        for i in range(len(response["Reservations"])):
            listTmp.append(response["Reservations"][i]["Instances"])
        json.dump(listTmp, f, indent=2, default=str)


    bucket_name = bucketName 
    key = objectName + ".json"

    # Uploading the json file into s3 bucket
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file("upload.json", key)
    location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)['LocationConstraint']

    # the Url of the file stored in the bucket
    url = "https://s3-%s.amazonaws.com/%s/%s" % (location, bucket_name, key)

    return url

if __name__ == "__main__":

    # usage python getLink.py -b <bucket name> -o <object name> -i <instance ids>

    # Instance ids can be more than one and if written 
    # python getLink.py -b <bucket name> -o <object name> -i all   
    # gets all instances metadata

    parser = argparse.ArgumentParser(description='Get URL of the EC2 instance metadata')
    parser.add_argument('-b','--bucketName', help='<Required> Set flag', required=True)
    parser.add_argument('-o','--objectName', help='<Required> Set flag', required=True)
    parser.add_argument('-i','--instanceIDs', nargs="+", help='<Required> Set flag', required=True)
    args = parser.parse_args()
    print("bucket name - " + args.bucketName)
    print("output name - " + args.objectName)
    print("instance IDs - ",  args.instanceIDs)

    data_url = getDataLink(args.bucketName, args.objectName, args.instanceIDs)
    print("output Link - " + data_url)
