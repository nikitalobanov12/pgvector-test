variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-west-2"
}

variable "instance_type" {
  description = "EC2 instance type for the FastAPI host"
  type        = string
  default     = "t3.micro"
}

variable "root_volume_size" {
  description = "Root volume size (GB) for the EC2 instance"
  type        = number
  default     = 30
}

variable "instance_name" {
  description = "Name tag applied to the EC2 instance"
  type        = string
  default     = "embedding-test"
}

variable "key_pair_name" {
  description = "Existing EC2 key pair name for SSH access"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "CIDR block allowed to access the instance over SSH"
  type        = string
}

variable "app_repository_url" {
  description = "Git repository URL containing the FastAPI project"
  type        = string
}

variable "app_branch" {
  description = "Git branch to check out for the application"
  type        = string
  default     = "master"
}

variable "db_username" {
  description = "PostgreSQL username used by the app and container"
  type        = string
  default     = "dev"
}

variable "db_password" {
  description = "PostgreSQL password used by the app and container"
  type        = string
  default     = "dev"
  sensitive   = true
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "vecdb"
}

variable "model_name" {
  description = "SentenceTransformers model identifier"
  type        = string
  default     = "all-MiniLM-L6-v2"
}

variable "common_tags" {
  description = "Tags applied to all taggable resources"
  type        = map(string)
  default = {
    Project = "embedding-demo"
  }
}
