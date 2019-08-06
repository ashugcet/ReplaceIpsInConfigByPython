
#!/usr/bin/python
import boto3
import sys
Key1= sys.argv[1] 
Key2= sys.argv[2] 
boto3.setup_default_session(profile_name='default')
def list_instances_by_tag_value(tagkey, tagvalue):
 ec2client = boto3.client('ec2',region_name='eu-west-1')
 response = ec2client.describe_instances(
 Filters=[
 {
 'Name': 'tag:'+tagkey,
 'Values': [tagvalue]
 }
 ]
 )
 ips=[]
 for reservation in (response["Reservations"]):
  for instance in reservation["Instances"]:
   ips.append(instance["PrivateIpAddress"])
 return ips
mm_iplist=list_instances_by_tag_value(Key1,Key2)

#print("\nActual master Ips:", mm_iplist)

with open("ectd.config","r+") as etcdconfig:
 new_etcdconfig = etcdconfig.readlines()
 etcdconfig.seek(0)
 for line in new_etcdconfig:
  if "k8s-master-" not in line:
    etcdconfig.write(line)
 etcdconfig.truncate()
 i=0
 for ip in mm_iplist:
  etcdconfig.write("server k8s-master-"+str(i)+" "+ip+":6443 check fall 3 rise 2\n")
  i+=1

