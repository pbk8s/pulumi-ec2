import pulumi
import pulumi_tls as tls
import pulumi_command as command
import pulumi_aws as aws

# EC2 instance
size = 'm6g.2xlarge'

ssh_key = tls.PrivateKey(
    "p1-key",
    algorithm="RSA",
    rsa_bits=4096,
)

aws_key = aws.ec2.KeyPair(
    "p1-key",
    key_name="p1-key",
    public_key=ssh_key.public_key_openssh,
    opts=pulumi.ResourceOptions(parent=ssh_key),
)

# Graviton Ubuntu 22.04 AMI
ubuntu = aws.ec2.get_ami(most_recent=True,
    filters=[
        aws.ec2.GetAmiFilterArgs(
            name="name",
            values=["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-arm64-server-*"],
        ),
    ],
    owners=["099720109477"])

# Create new VPC
vpc = aws.ec2.Vpc("p1-vpc",
    cidr_block="172.16.0.0/16",
    enable_dns_hostnames=True,
    tags={
        "Name": "p1-vpc",
    })

# Create new subnet
subnet = aws.ec2.Subnet("p1-subnet",
    vpc_id=vpc.id,
    cidr_block="172.16.0.0/24",
    availability_zone="us-east-1a",
    map_public_ip_on_launch=True,
    tags={
        "Name": "p1-subnet",
    })

# Create new internet gateway
igw = aws.ec2.InternetGateway(
	"p1-igw",
	vpc_id=vpc.id,
)

# Create new route table
route_table = aws.ec2.RouteTable(
	"p1-route-table",
	vpc_id=vpc.id,
	routes=[
		{
			"cidr_block": "0.0.0.0/0",
			"gateway_id": igw.id
		}
	]
)

# Associate route table with subnet
rt_assoc = aws.ec2.RouteTableAssociation(
	"p1-rta",
	route_table_id=route_table.id,
	subnet_id=subnet.id
)

# To use an existing VPC
#vpc = aws.ec2.Vpc.get(resource_name="simple-vpc", id="vpc-030c68e465b57a3ba")

# To use an existing subnet
#subnet =  aws.ec2.get_subnet(filters=[aws.ec2.GetSubnetFilterArgs(
#    name="tag:Name",
#    values=["Public subnet"],
#)])

# Create new security group
group = aws.ec2.SecurityGroup('p1-security-grouup',
    vpc_id=vpc.id,
    description='Enable HTTP and SSH access',
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
        protocol='tcp',
        from_port=80,
        to_port=80,
        cidr_blocks=['0.0.0.0/0'],),
        aws.ec2.SecurityGroupIngressArgs(
        protocol='tcp',
        from_port=22,
        to_port=22,
        cidr_blocks=['0.0.0.0/0'],),
    ],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )]
    )

# Finally, new EC2 instance
server = aws.ec2.Instance('p1-server',
        tags={
            "Name": "p1",
            },
    instance_type=size,
    key_name=aws_key.key_name,
    vpc_security_group_ids=[group.id],
    subnet_id=subnet.id,
    ami=ubuntu.id)

connection = command.remote.ConnectionArgs(
    host=server.public_ip,
    user='ubuntu',
    private_key=ssh_key.private_key_openssh,
)

# Copy a file to the new server
copy_script = command.remote.CopyFile('p1-copy-script',
    connection=connection,
    local_path='install-mongodb.sh',
    remote_path='install-mongodb.sh',
    opts=pulumi.ResourceOptions(depends_on=[server]),
)

# Copy gatord binary
copy_script = command.remote.CopyFile('gatord-copy',
    connection=connection,
    local_path='gatord',
    remote_path='gatord',
    opts=pulumi.ResourceOptions(depends_on=[server]),
)

# Execute a basic command on our server.
run_script = command.remote.Command('p1-run-script',
    connection=connection,
    create='bash ./install-mongodb.sh',
    opts=pulumi.ResourceOptions(depends_on=[copy_script]),
)

# Output the public IP and DNS name
pulumi.export('public_ip', server.public_ip)
pulumi.export('public_dns', server.public_dns)
pulumi.export('private_key_pem', ssh_key.private_key_pem)
