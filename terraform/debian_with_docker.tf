resource "digitalocean_droplet" "dummy_ops_on_docker" {
    # you can set 'ubuntu-22-04-x64' image too without changing anything.
    image = "debian-12-x64"
    name = "${var.your_virtual_machine_hostname}"
    region = "fra1"
    size = "s-1vcpu-1gb"
    ssh_keys = [
      data.digitalocean_ssh_key.terraform.id
    ]
    tags = ["dummy-fastapi-flask-ops"]

    connection {
      host = self.ipv4_address
      user = "root"
      type = "ssh"
      private_key = file(var.pvt_key)
      timeout = "2m"
    }

    provisioner "remote-exec" {
      inline = [
        "export PATH=$PATH:/usr/bin",
        "sudo apt update -y",
        "sudo apt install tree ca-certificates curl gnupg snapd ufw net-tools dnsutils netcat-traditional lynis -y",
        "sudo apt install acct sysstat auditd chkrootkit fail2ban libpam-pwquality -y",
        "sudo apt install python3-protobuf libcrack2 apt-show-versions debsums libpam-tmpdir apt-listbugs openssl -y",
        "sudo install -m 0755 -d /etc/apt/keyrings",
        # Add Docker's official GPG key:
        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg",
        "sudo chmod a+r /etc/apt/keyrings/docker.gpg",
        "sudo wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg",
        # To update for architecture and os
        "sudo echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com bookworm main' > /etc/apt/sources.list.d/hashicorp.list",
        "sudo apt install docker docker-compose ufw -y",
        "sudo ufw --force enable",
        "sudo ufw allow ssh",
        "sudo ufw allow http",
        "sudo ufw allow https",
        "sudo ufw allow 8200",
        "sudo systemctl enable --now sysstat",
        "sudo systemctl enable --now auditd",
        "sudo systemctl enable --now fail2ban",
        "sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local",
        "sudo echo 'install usb-storage /bin/true' > /etc/modprobe.d/fake_usb.conf",
        "sudo mkdir /etc/ssl/dhparam/",
        "sudo openssl dhparam -out /etc/ssl/dhparam/dhparam.pem 4096",
        # We create a dummy_user
        "useradd dummy_user",
        "mkdir -p /home/${var.dummy_username}/.ssh",
        "cp /etc/skel/.bash* /home/${var.dummy_username}/",
        "cp /etc/skel/.profile /home/${var.dummy_username}/",
        "echo '${var.your_ssh_public_key}' >> /home/${var.dummy_username}/.ssh/authorized_keys",
        "mkdir -p /home/${var.dummy_username}/vault/config",
        "mkdir /home/${var.dummy_username}/vault/policies",
        "mkdir /home/${var.dummy_username}/vault/scripts",
        "chown -R ${var.dummy_username}: /home/${var.dummy_username}/",
        "usermod -aG docker ${var.dummy_username}",
        "chsh -s /bin/bash ${var.dummy_username}",
      ]
    }

    provisioner "file" {
        source      = "files/bashrc"
        destination = "/root/.bashrc"
    }

    provisioner "file" {
        source      = "files/bashrc"
        destination = "/home/${var.dummy_username}/.bashrc"
    }

    provisioner "file" {
        source      = "files/profile"
        destination = "/home/${var.dummy_username}/.profile"
    }

    provisioner "file" {
        source      = "files/etc_issue"
        destination = "/etc/issue"
    }

    provisioner "file" {
        source      = "files/etc_issue_net"
        destination = "/etc/issue.net"
    }

    provisioner "file" {
        source      = "files/sshd_config"
        destination = "/etc/ssh/sshd_config"
    }

    provisioner "file" {
        source      = "files/purge_docker_at_boot"
        destination = "/etc/init.d/purge_docker_at_boot"
    }

    provisioner "file" {
        content      = templatefile("files/vault/config/vault-config.json.tftpl", {host_fqdn=var.host_fqdn})
        destination = "/home/${var.dummy_username}/vault/config/vault-config.json"
    }

    provisioner "file" {
        source      = "files/vault/policies/gitlab.json"
        destination = "/home/${var.dummy_username}/vault/policies/gitlab.json"
    }

    provisioner "file" {
        content      = templatefile("files/vault/scripts/build_it_up.sh.tftpl", var.vault_script_vars)
        destination = "/home/${var.dummy_username}/vault/scripts/build_it_up.sh"
    }

    provisioner "file" {
        source      = "files/vault/Dockerfile"
        destination = "/home/${var.dummy_username}/vault/Dockerfile"
    }

    provisioner "remote-exec" {
        inline = [
          "chown -R ${var.dummy_username}: /home/${var.dummy_username}/",
          "ln -s /etc/init.d/purge_docker_at_boot /etc/rc0.d/S01purge-any-remaining-docker",
          "ln -s /etc/init.d/purge_docker_at_boot /etc/rc5.d/S01purge-any-remaining-docker"
        ]
    }
}
