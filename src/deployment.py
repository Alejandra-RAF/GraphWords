import boto3

AWS_REGION = "us-east-1"
BUCKET_NAME = "deployments-bucket456"
FILE_PATH_DATALEKE = "src/utility_scripts/create_datalake.py"
FILE_PATH_DATAMART = "src/utility_scripts/create_datamart.py"
FILE_PATH_GRAPH = "src/utility_scripts/create_graph.py"
FILE_PATH_API = "src/utility_scripts/create_api.py"
FILE_PATH_FUNCTIONS_API = "src/utility_scripts/create_functions_api.py"

AMI_ID = "ami-0fff1b9a61dec8a5f"
INSTANCE_TYPE = "t2.micro"
KEY_NAME = "vockey"
ROLE_NAME = "LabInstanceProfile"

s3 = boto3.client('s3', region_name=AWS_REGION)
ec2 = boto3.resource('ec2', region_name=AWS_REGION)
elbv2_client = boto3.client('elbv2', region_name=AWS_REGION)

def upload_script_to_s3():
    print(f"Subiendo scripts al bucket {BUCKET_NAME}...")
    s3.create_bucket(Bucket=BUCKET_NAME)
    files = {
        "create_datalake.py": FILE_PATH_DATALEKE,
        "create_datamart.py": FILE_PATH_DATAMART,
        "create_graph.py": FILE_PATH_GRAPH,
        "create_api.py": FILE_PATH_API,
        "create_functions_api.py": FILE_PATH_FUNCTIONS_API,
    }
    for key, path in files.items():
        s3.upload_file(path, BUCKET_NAME, key)
    print("Archivos subidos correctamente.")

def create_vpc():
    print("Creando VPC y recursos de red...")
    vpc = ec2.create_vpc(CidrBlock="10.0.0.0/16")
    vpc.wait_until_available()
    vpc.create_tags(Tags=[{"Key": "Name", "Value": "GraphWordVPC"}])
    print(f"VPC creada con ID: {vpc.id}")

    subnet1 = vpc.create_subnet(CidrBlock="10.0.1.0/24", AvailabilityZone=f"{AWS_REGION}a")
    subnet2 = vpc.create_subnet(CidrBlock="10.0.2.0/24", AvailabilityZone=f"{AWS_REGION}b")
    print(f"Subred 1 creada con ID: {subnet1.id}")
    print(f"Subred 2 creada con ID: {subnet2.id}")

    igw = ec2.create_internet_gateway()
    vpc.attach_internet_gateway(InternetGatewayId=igw.id)
    print(f"Internet Gateway creado con ID: {igw.id}")

    route_table = vpc.create_route_table()
    route_table.create_route(DestinationCidrBlock="0.0.0.0/0", GatewayId=igw.id)
    route_table.associate_with_subnet(SubnetId=subnet1.id)
    route_table.associate_with_subnet(SubnetId=subnet2.id)

    sg = ec2.create_security_group(
        GroupName="graphword-sg",
        Description="Permitir SSH, HTTP y HTTPS",
        VpcId=vpc.id
    )
    sg.authorize_ingress(
        IpPermissions=[
            {'FromPort': 22, 'ToPort': 22, 'IpProtocol': 'tcp', 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'FromPort': 80, 'ToPort': 80, 'IpProtocol': 'tcp', 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'FromPort': 5000, 'ToPort': 5000, 'IpProtocol': 'tcp', 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ]
    )
    print(f"Grupo de seguridad creado con ID: {sg.id}")

    return vpc.id, [subnet1.id, subnet2.id], sg.id

def create_load_balancer(vpc_id, subnet_ids, sg_id):
    print("Creando Load Balancer...")
    lb = elbv2_client.create_load_balancer(
        Name="GraphWordALB",
        Subnets=subnet_ids,
        SecurityGroups=[sg_id],
        Scheme='internet-facing',
        Tags=[{'Key': 'Name', 'Value': 'GraphWordALB'}],
        Type='application',
        IpAddressType='ipv4'
    )
    lb_arn = lb['LoadBalancers'][0]['LoadBalancerArn']
    lb_dns_name = lb['LoadBalancers'][0]['DNSName']  
    print(f"Load Balancer creado con ARN: {lb_arn}")
    print(f"DNS público del Load Balancer: http://{lb_dns_name}")

    target_group = elbv2_client.create_target_group(
        Name='GraphWordTG1',
        Protocol='HTTP',
        Port=5000,
        VpcId=vpc_id,
        HealthCheckProtocol='HTTP',
        HealthCheckPort='5000',
        HealthCheckPath='/',
        HealthCheckIntervalSeconds=30,
        HealthCheckTimeoutSeconds=5,
        HealthyThresholdCount=2,
        UnhealthyThresholdCount=2,
        TargetType='instance'
    )
    target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']
    print(f"Target Group creado con ARN: {target_group_arn}")

    listener = elbv2_client.create_listener(
        LoadBalancerArn=lb_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[{
            'Type': 'forward',
            'TargetGroupArn': target_group_arn
        }]
    )
    print(f"Listener creado con ARN: {listener['Listeners'][0]['ListenerArn']}")

    return target_group_arn, lb_dns_name

def launch_ec2_instances(target_group_arn, subnet_ids, sg_id):
    instance_ids = []
    public_ips = []

    for subnet_id in subnet_ids:
        print(f"Lanzando instancia EC2 en la subnet {subnet_id}...")
        instance = ec2.create_instances(
            ImageId=AMI_ID,
            InstanceType=INSTANCE_TYPE,
            KeyName=KEY_NAME,
            MinCount=1,
            MaxCount=1,
            NetworkInterfaces=[{
                'SubnetId': subnet_id,
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': True,
                'Groups': [sg_id]
            }],
            IamInstanceProfile={
                'Name': ROLE_NAME
            },
            UserData=f"""#!/bin/bash
            yum install -y python3-pip
            pip3 install boto3 Flask
            aws s3 cp s3://{BUCKET_NAME}/create_datalake.py /home/ec2-user/create_datalake.py
            python3 /home/ec2-user/create_datalake.py
            aws s3 cp s3://{BUCKET_NAME}/create_datamart.py /home/ec2-user/create_datamart.py
            python3 /home/ec2-user/create_datamart.py
            aws s3 cp s3://{BUCKET_NAME}/create_graph.py /home/ec2-user/create_graph.py
            python3 /home/ec2-user/create_graph.py
            aws s3 cp s3://{BUCKET_NAME}/create_api.py /home/ec2-user/create_api.py
            aws s3 cp s3://{BUCKET_NAME}/create_functions_api.py /home/ec2-user/create_functions_api.py
            python3 /home/ec2-user/create_api.py
            """,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': f'GraphWord-Instance-{subnet_id}'}]
            }]
        )[0]

        instance.wait_until_running()
        instance.load()
        print(f"Instancia EC2 creada con IP pública: {instance.public_ip_address} en subnet {subnet_id}")

        elbv2_client.register_targets(
            TargetGroupArn=target_group_arn,
            Targets=[{'Id': instance.id}]
        )
        print(f"Instancia {instance.id} registrada en el Target Group.")

        instance_ids.append(instance.id)
        public_ips.append(instance.public_ip_address)

    return instance_ids, public_ips

if __name__ == "__main__":
    upload_script_to_s3()
    vpc_id, subnet_ids, sg_id = create_vpc()
    target_group_arn, lb_dns_name = create_load_balancer(vpc_id, subnet_ids, sg_id)
    instance_ids, public_ips = launch_ec2_instances(target_group_arn, subnet_ids, sg_id)
    print(f"¡Despliegue completo! Instancias lanzadas: {instance_ids}")
    print(f"\nPara realizar consultas, usa la siguiente URL: http://{lb_dns_name}")
