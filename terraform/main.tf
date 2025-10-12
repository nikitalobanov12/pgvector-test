terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }

  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

locals {
  selected_subnet_id = element(data.aws_subnets.default.ids, 0)

  docker_compose = templatefile("${path.module}/docker-compose.yaml.tftpl", {
    db_username = var.db_username
    db_password = var.db_password
    db_name     = var.db_name
    model_name  = var.model_name
  })

  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    docker_compose = local.docker_compose
    app_repo_url   = replace(var.app_repository_url, "\"", "\\\"")
    app_branch     = replace(var.app_branch, "\"", "\\\"")
  })
}

resource "aws_security_group" "app" {
  name_prefix = "embedding-sg-"
  description = "Security group for embedding API EC2 host"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }

  ingress {
    description      = "HTTP access"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    description      = "Outbound access"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = merge(var.common_tags, {
    Name = "${var.instance_name}-sg"
  })
}

data "aws_ami" "amazon_linux" {
  owners      = ["amazon"]
  most_recent = true

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  subnet_id                   = local.selected_subnet_id
  key_name                    = var.key_pair_name
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = true
  user_data                   = local.user_data

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp3"
    encrypted   = true
  }

  tags = merge(var.common_tags, {
    Name = var.instance_name
  })
}
