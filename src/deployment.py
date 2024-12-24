import boto3
import subprocess
import os
import time
import json

# Crear clientes para AWS y LocalStack
ec2_client = boto3.client('ec2')
elb_client = boto3.client('elbv2')
autoscaling_client = boto3.client('autoscaling')
s3 = boto3.client("s3", endpoint_url="http://localhost:4566")
lambda_client = boto3.client('lambda', endpoint_url='http://localhost:4566')  # LocalStack
apigateway_client = boto3.client('apigateway')  # Cliente para API Gateway

# Crear VPC
def create_vpc():
    response = ec2_client.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = response['Vpc']['VpcId']
    ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
    ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
    print(f'VPC creada con ID: {vpc_id}')
    return vpc_id

# Crear Subnets
def create_subnet(vpc_id, cidr_block, availability_zone, auto_assign_ip=False):
    response = ec2_client.create_subnet(
        VpcId=vpc_id,
        CidrBlock=cidr_block,
        AvailabilityZone=availability_zone
    )
    subnet_id = response['Subnet']['SubnetId']
    print(f'Subnet creada con ID: {subnet_id} en {availability_zone}')
    
    if auto_assign_ip:
        ec2_client.modify_subnet_attribute(
            SubnetId=subnet_id,
            MapPublicIpOnLaunch={'Value': True}
        )
        print(f'Asignación automática de IP pública habilitada para la Subnet {subnet_id}')
    
    return subnet_id

# Crear Internet Gateway
def create_internet_gateway(vpc_id):
    response = ec2_client.create_internet_gateway()
    igw_id = response['InternetGateway']['InternetGatewayId']
    ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    print(f'Internet Gateway creado con ID: {igw_id}')
    return igw_id

# Crear tabla de rutas
def create_route_table(vpc_id, igw_id):
    response = ec2_client.create_route_table(VpcId=vpc_id)
    route_table_id = response['RouteTable']['RouteTableId']
    ec2_client.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw_id
    )
    print(f'Tabla de rutas creada con ID: {route_table_id}')
    return route_table_id

# Asociar tabla de rutas a una subnet
def associate_route_table(route_table_id, subnet_id):
    ec2_client.associate_route_table(RouteTableId=route_table_id, SubnetId=subnet_id)
    print(f'Tabla de rutas asociada con la Subnet {subnet_id}')

# Crear Security Group
def create_security_group(vpc_id):
    response = ec2_client.create_security_group(
        GroupName='SG-OrderService',
        Description='Security group for Order Service',
        VpcId=vpc_id
    )
    sg_id = response['GroupId']
    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )
    print(f'Grupo de seguridad creado con ID: {sg_id}')
    return sg_id

# Crear Load Balancer
def create_load_balancer(subnet_ids, sg_id):
    lb_name = f"order-service-lb-{int(time.time())}"
    response = elb_client.create_load_balancer(
        Name=lb_name,
        Subnets=subnet_ids,
        SecurityGroups=[sg_id],
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4'
    )
    lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    print(f'Load Balancer creado con ARN: {lb_arn}')
    return lb_arn

# Crear Target Group
def create_target_group(vpc_id):
    tg_name = f"order-service-tg-{int(time.time())}"
    response = elb_client.create_target_group(
        Name=tg_name,
        Protocol='HTTP',
        Port=80,
        VpcId=vpc_id,
        TargetType='instance'
    )
    tg_arn = response['TargetGroups'][0]['TargetGroupArn']
    print(f'Target Group creado con ARN: {tg_arn}')
    return tg_arn

# Crear Listener para el Load Balancer
def create_listener(lb_arn, tg_arn):
    elb_client.create_listener(
        LoadBalancerArn=lb_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[{
            'Type': 'forward',
            'TargetGroupArn': tg_arn
        }]
    )
    print('Listener creado y asociado al Load Balancer')

# Crear Launch Configuration con UserData
def create_launch_configuration_with_userdata(sg_id):
    UserData = """#!/bin/bash
        yum install -y aws-cli
        yum install -y curl
        echo "UserData ejecutado correctamente."
    """
    autoscaling_client.create_launch_configuration(
        LaunchConfigurationName='order-service-lc',
        ImageId='ami-0fff1b9a61dec8a5f',  
        InstanceType='t2.micro',
        SecurityGroups=[sg_id],
        UserData=UserData
    )
    print('Launch Configuration creada con UserData')

# Crear Auto Scaling Group
def create_auto_scaling_group(subnet_ids, tg_arn):
    autoscaling_client.create_auto_scaling_group(
        AutoScalingGroupName='order-service-asg',
        LaunchConfigurationName='order-service-lc',
        MinSize=1,
        MaxSize=3,
        DesiredCapacity=1,
        VPCZoneIdentifier=','.join(subnet_ids),
        TargetGroupARNs=[tg_arn]
    )
    print('Auto Scaling Group creado')

# Ejecutar un script `Create_Lamdba_*` para Lambdas Locales
def execute_create_lambda(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
        print(f"Script '{script_name}' ejecutado exitosamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar '{script_name}': {e}")

# Invocar Lambda Local
def invoke_lambda(function_name, payload):
    try:
        print(f"Invocando Lambda '{function_name}' con payload: {payload}")
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        result = response['Payload'].read().decode('utf-8')
        print(f"Resultado de invocar '{function_name}': {result}")
    except Exception as e:
        print(f"Error al invocar la Lambda '{function_name}': {e}")

# Crear API Gateway
def create_api_gateway(api_name):
    response = apigateway_client.create_rest_api(name=api_name)
    api_id = response['id']
    print(f"API Gateway creado con ID: {api_id}")
    return api_id

# Obtener el ID del recurso raíz
def get_root_resource_id(api_id):
    response = apigateway_client.get_resources(restApiId=api_id)
    root_id = next(item['id'] for item in response['items'] if item['path'] == '/')
    print(f"ID del recurso raíz: {root_id}")
    return root_id

# Configurar recurso y método GET
def create_resource_and_method(api_id, root_id, path_part, lambda_arn):
    response = apigateway_client.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart=path_part
    )
    resource_id = response['id']
    print(f"Recurso creado con ID: {resource_id} y path: {path_part}")
    
    apigateway_client.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='GET',
        authorizationType='NONE'
    )
    apigateway_client.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='GET',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
    )
    print(f"Método GET configurado para {path_part}. Lambda URI: arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations")
    return resource_id

# Desplegar API
def deploy_api(api_id, stage_name):
    response = apigateway_client.create_deployment(
        restApiId=api_id,
        stageName=stage_name
    )
    print(f"API desplegada en la etapa {stage_name}")
    api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/{stage_name}"
    print(f"URL de la API: {api_url}")
    return response['id']


# Flujo Principal
def main():
    # Configuración básica en AWS
    vpc_id = create_vpc()
    subnet_public_1 = create_subnet(vpc_id, '10.0.0.0/24', 'us-east-1a', auto_assign_ip=True)
    subnet_public_2 = create_subnet(vpc_id, '10.0.3.0/24', 'us-east-1b', auto_assign_ip=True)
    igw_id = create_internet_gateway(vpc_id)
    route_table_id = create_route_table(vpc_id, igw_id)
    associate_route_table(route_table_id, subnet_public_1)
    associate_route_table(route_table_id, subnet_public_2)
    sg_id = create_security_group(vpc_id)
    lb_arn = create_load_balancer([subnet_public_1, subnet_public_2], sg_id)
    tg_arn = create_target_group(vpc_id)
    create_listener(lb_arn, tg_arn)
    create_launch_configuration_with_userdata(sg_id)
    create_auto_scaling_group([subnet_public_1, subnet_public_2], tg_arn)

     # Implementación de API Gateway
    api_name = "MyAPI"
    api_id = create_api_gateway(api_name)
    root_id = get_root_resource_id(api_id)
    lambda_arn = "arn:aws:lambda:us-east-1:000000000000:function:LambdaScriptApi"  # ARN de la Lambda API
    resource_id = create_resource_and_method(api_id, root_id, "Dijkstra", lambda_arn)
    deploy_api(api_id, "test")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Scripts `Create_Lamdba_*` para configurar Lambdas locales
    create_scripts = [
        os.path.join(BASE_DIR, "lambdas/create_lambda_datalake.py"),
        os.path.join(BASE_DIR, "lambdas/create_lambda_datamart.py"),
        os.path.join(BASE_DIR, "lambdas/create_lambda_graph.py"),
        os.path.join(BASE_DIR, "lambdas/create_lambda_api.py")
    ]
    
    for script in create_scripts:
        execute_create_lambda(script)

    # Invocar Lambdas creadas en LocalStack
    lambdas_to_invoke = [
        {"name": "LambdaScriptDatalake", "payload": {"action": "process_datalake"}},
        {"name": "LambdaScriptDatamart", "payload": {"action": "process_datamart"}},
        {"name": "LambdaScriptGraph", "payload": {"action": "process_graph"}},
        {"name": "LambdaScriptApi", "payload": {"action": "serve_api"}}
    ]
    
    for lambda_config in lambdas_to_invoke:
        print(f"Invocando {lambda_config['name']}...")
        invoke_lambda(lambda_config["name"], lambda_config["payload"])

if __name__ == '__main__':
    main()
