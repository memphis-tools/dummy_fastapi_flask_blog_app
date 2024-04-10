resource "digitalocean_firewall" "dummy_ops_on_docker_firewall" {
  name  = "${var.host_fqdn}-terraform-firewall"
  droplet_ids = [digitalocean_droplet.dummy_ops_on_docker.id]

  inbound_rule {
      protocol                = "tcp"
      port_range              = "22"
      source_addresses        = ["0.0.0.0/0", "::/0"]
    }
  inbound_rule {
      protocol                = "tcp"
      port_range              = "8200"
      source_addresses        = ["0.0.0.0/0", "::/0"]
    }
  inbound_rule {
      protocol                = "tcp"
      port_range              = "80"
      source_addresses        = ["0.0.0.0/0", "::/0"]
    }
  inbound_rule {
      protocol                = "tcp"
      port_range              = "443"
      source_addresses        = ["0.0.0.0/0", "::/0"]
    }

  outbound_rule {
      protocol                = "tcp"
      port_range              = "all"
      destination_addresses   = ["0.0.0.0/0", "::/0"]
    }
  outbound_rule {
      protocol                = "udp"
      port_range              = "all"
      destination_addresses   = ["0.0.0.0/0", "::/0"]
    }
  outbound_rule {
      protocol                = "icmp"
      destination_addresses   = ["0.0.0.0/0", "::/0"]
    }
}
