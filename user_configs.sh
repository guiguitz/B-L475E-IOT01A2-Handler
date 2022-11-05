# Please, set the aws region which your aws lambda is located.
echo "-> Configuring the aws region:"
aws configure set default.region us-east-1
aws configure get default.region
