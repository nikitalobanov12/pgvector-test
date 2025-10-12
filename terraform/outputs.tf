output "instance_public_ip" {
  description = "Public IPv4 address of the embedding API EC2 instance"
  value       = aws_instance.app.public_ip
}

output "ssh_connection" {
  description = "Convenience SSH command"
  value       = "ssh -i /path/to/${var.key_pair_name}.pem ec2-user@${aws_instance.app.public_ip}"
}

output "healthcheck_url" {
  description = "HTTP health check URL"
  value       = format("http://%s/healthz", aws_instance.app.public_ip)
}
