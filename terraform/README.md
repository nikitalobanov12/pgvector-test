# Terraform Bootstrap (AWS EC2 + Docker Compose)

This configuration provisions a single EC2 instance in AWS (`us-west-2` by default) that runs the FastAPI embedding service and a PostgreSQL + pgvector container via Docker Compose.

## Prerequisites
- Terraform >= 1.5
- AWS credentials exported or configured (with rights to create EC2 + security groups)
- An EC2 key pair in `us-west-2` for SSH access
- Public Git repository URL for this project (so the instance can `git clone` it)

## Usage
1. Copy the example variables file and fill in required values:
   ```bash
   cp terraform/example.tfvars terraform/terraform.tfvars
   ```
   Update `terraform.tfvars` with your key pair name, SSH-allowed CIDR (e.g., `203.0.113.4/32`), and repo URL.
2. Initialize Terraform:
   ```bash
   cd terraform
   terraform init
   ```
3. Review the execution plan:
   ```bash
   terraform plan
   ```
4. Apply the configuration:
   ```bash
   terraform apply
   ```
5. After ~2 minutes, the outputs will include a health-check URL. Hit it with curl or a browser:
   ```bash
   curl http://<public-ip>/healthz
   ```
6. When finished, destroy the resources to stay within the free tier:
   ```bash
   terraform destroy
   ```

## Customisation
- `instance_type`: defaults to `t3.micro`. Switch to `t2.micro` if the t3 credit pool is exhausted.
- `model_name`: set to any SentenceTransformers identifier available on Hugging Face.
- `db_username`, `db_password`, `db_name`: adjust if you want non-default credentials.

## Notes
- Docker Compose writes a named volume (`pg_data`), which lives on the EC2 root volume. Root volume size is configurable via `root_volume_size` (default: 20 GB).
- The instance exposes HTTP on port 80. For HTTPS, add an Application Load Balancer or configure a reverse proxy + certificate.
- SSH is restricted to the CIDR you provide. Update `ssh_allowed_cidr` as your IP changes.
