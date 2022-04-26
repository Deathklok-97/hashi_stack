Nomad
1. Provision Computer Resources (3-5 Nomad Servers) (1-1000 Clients) x
2. Install the Nomad Binary x
3. Configure systemd x
4. Create Nomad Config Files x
5. Choose a Clustering Option x
6. Enable Gossip Encryption
7. Enable mTLS Encryption
8. Enable ACLs
9. Start Nomad x
10. Bootstrap the Initial ACL Token
11. Add policies

port used for used where
4646 HTTP APi API client calls to Agents
4647 RPC agent to agent
4648 TCP/UDP Serf(gossip) Server to Server
20000-32000 TCP/UDP Dynamic ports Inbound traffic to Clients

download https://www.nomadproject.io/downloads
unzip it
Set permissions on the binary - sudo chown root:root nomad
Move into path sudo mv nomad /usr/local/bin/
Confirm install nomad version

Install any task driver software
Docker, java, Qemu

make nomad service file at 
/etc/systemd/system/nomad.service

contents: 

[Unit]
Description=Nomad
Documentation=https://www.nomadproject.io/docs
Wants=network-online.target
After=network-online.target

[Service]
ExecReload=/bin/kill -HUP $MAINPID
ExecStart=/usr/local/bin/nomad agent -config /etc/nomad.d
KillMode=process
KillSignal=SIGINT
LimitNOFILE=infinity
LimitNPROC=infinity
Restart=on-failure
RestartSec=2
StartLimitBurst=3
StartLimitIntervalSec=10
TasksMax=infinity

[Install]
WantedBy=multi-user.target


create config dir
sudo mkdir --parents /etc/nomad.d

sudo chmod 700 /etc/nomad.d

sudo touch /etc/nomad.d/nomad.hcl

contents 
datacenter = "dc1"
data_dir = "/opt/nomad"

Only on Server config 
create config file at 
/etc/nomad.d/server.hcl

sudo touch /etc/nomad.d/server.hcl

server {
  enabled = true
  bootstrap_expect = 3
}

Client Configuration
sudo touch /etc/nomad.d/client.hcl

client {
  enabled = true
}

Clustering 
server {
	...
	server_join {
		retry_join = ["server ip"]
	}
}

client {
	...
	server_join {
		retry_join = ["server ip"]
	}
}

If using Consul, it just works

Enable ACLs
Add config to /etc/nomad.d/nomad.hcl

acl {
	enable = true
}

nomad acl bootstrap to get initial token

Hands on Lab 
https://katacode.com/hashicorp/courses/securing-nomad
https://learn.hashicorp.com/nomad

Start Nomad
sudo systemctl enable nomad
sudo systemctl start nomad
sudo systemctl status nomad

namespace "default" {
	policy = read,
	capabilities = ["submit-job","dispatch-job","read-logs"]
}

#push hcl policy 
nomad acl policy apply \
  -description "Application Developer policy" \
  app-dev app-dev_policy.hcl

#Create app dev token
nomad acl token create -name="Test app-dev token" \
  -policy=app-dev -type=client | tee ~/app-dev.token


nomad acl policy apply \
  -description "Production Operations policy" \
  prod-ops prod-ops_policy.hcl


nomad acl token create -name="Test prod-ops token" \
  -policy=prod-ops -type=client | tee ~/prod-ops.token


{# NOMAD_CACERT=/etc/nomad.d/tls/nomad-agent-ca.pem
NOMAD_CLIENT_CERT=/root/tls/global-cli-nomad-0.pem
NOMAD_CLIENT_KEY=/root/tls/global-cli-nomad-0-key.pem
NOMAD_NODE_NAME=nomad-server-1
NOMAD_ADDR=https://127.0.0.1:4646
NOMAD_TOKEN=f0b0a2b8-b465-2c2a-48f2-d708f1317e50

curl --cert ${NOMAD_CLIENT_CERT} \
  --key ${NOMAD_CLIENT_KEY} \
  --cacert ${NOMAD_CACERT} \
  --header "X-Nomad-Token: ${NOMAD_TOKEN}" \
  ${NOMAD_ADDR}/v1/nodes #}



#Generate Nomad Tokens with HashiCorp Vault

nomad 

Enable the nomad secrets backend in Vault:
vault secrets enable nomad

Once you have the Nomad secret backend enabled, configure access with Nomad's address and management token:
vault write nomad/config/access \
    address=http://127.0.0.1:4646 \
    token=adf4238a-882b-9ddc-4a9d-5b6758e4159e

Vault secrets engines have the concept of roles, 
which are configuration units that group one or more Vault policies to a potential identity attribute, (e.g. LDAP Group membership). 
The name of the role is specified on the path, while the mapping to policies is done by naming them in a comma separated list, for example:
vault write nomad/role/role-name policies=policyone,policytwo

Similarly, to create management tokens, or global tokens:
vault write nomad/role/role-name type=management global=true

Create a Vault policy to allow different identities to get tokens associated with a particular role:

cat << EOF | vault policy write nomad-user-policy -
path "nomad/creds/role-name" {
  capabilities = ["read"]
}
EOF

If you have an existing authentication backend (like LDAP), 
follow the relevant instructions to create a role available on the Authentication backends page. 
Otherwise, for testing purposes, a Vault token can be generated associated with the policy:
vault token create -policy=nomad-user-policy

Finally obtain a Nomad Token using the existing Vault Token:
vault read nomad/creds/role-name

Verify that the token is created correctly in Nomad, looking it up by its accessor:
nomad acl token info 10b8fb49-7024-2126-8683-ab355b581db2