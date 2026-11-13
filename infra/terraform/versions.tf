terraform {
  # Pinned exactly; matches the checksum-verified binary installed in Cloud Shell.
  required_version = "= 1.17.2"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.11" # stay on the current major (8.x); exact build pinned in .terraform.lock.hcl
    }
  }
}
