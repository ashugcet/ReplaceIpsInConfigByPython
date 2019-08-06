
#!/usr/bin/python
import boto3
import sys
import subprocess
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
#print(mm_iplist)
print("\nActual master Ips:", mm_iplist)

master_ips = []
with open ('ectd.config', 'rt') as etcdconfig:
    for line in etcdconfig:
        master_ip_index = line.lower().replace(' ','').find('serverk8s-master-')        
        if master_ip_index != -1:
            #print(line.lower().replace(' ',''))
            #print(line.lower().replace(' ','').find('serverk8s-master-'))
            master_ip_end_index = line.lower().replace(' ','').find(':') 
            master_ips.append(line.lower().replace(' ','')[18:master_ip_end_index])
print("\nMaster Ips in config:", master_ips)
unmatchedips=[]
matchedips=[]
for ip in mm_iplist:
 if master_ips.count(ip) >= 1 :    
    matchedips.append(ip)    
 else :
     unmatchedips.append(ip)
   
print("\nMatched IPs:",matchedips)
print("\nUnmatched IPs:",unmatchedips)

if len(unmatchedips) > 0:
 with open("ectd.config","r+") as etcdconfig_to_be_changed:
  new_etcdconfig = etcdconfig_to_be_changed.readlines()
  etcdconfig_to_be_changed.seek(0)
  for line in new_etcdconfig:
   if "k8s-master-" not in line:
    etcdconfig_to_be_changed.write(line)
  etcdconfig_to_be_changed.truncate()
  i=0
  for ip in mm_iplist:
   etcdconfig_to_be_changed.write("server k8s-master-"+str(i)+" "+ip+":6443 check fall 3 rise 2\n")
   i+=1
  #command = ['service', 'haproxy', 'reload']
  #subprocess.call(command, shell=True)
 

