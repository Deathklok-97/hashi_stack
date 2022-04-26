
#Consul Notes

# rpc client server agents send/recv data in consul services k/v service mesh config etc
* 8300 open clients -> server  rpc port i.e. pulls lists from servers 
* 8300 open server to server 

# gossip managing cluster membership and distributed health checking 
* 8301 open clients only lan gossip between clients 

* 8500 need to open client + server tcp ingress
* 8501 for https client + server 

* 8600 for dns


* curl localhost:8500/v1/agent/services?pretty

* Why is gossip used versus rpc for everything?
* gossip makes very ephemeral short lived connections
* rpc are long lived and exchange more data, which requires more reliable communication like tcp

# Service *What?
* https://www.consul.io/docs/connect/config-entries/service-router
* https://www.consul.io/docs/connect/config-entries/service-splitter
* https://www.consul.io/docs/connect/config-entries/service-resolver

## ACL's

## Required privileges for datacenter operations
#### Below is a table with the minimum required privileges for a set of common operations. 
#### You can also use exact match rules when creating specific policies that are less flexible.


| CLI Operation                             | Required Privilege                                                    |
| ----------------------------------------- | --------------------------------------------------------------------- |
| consul reload                             | agent_prefix "": policy = "write"                                     |
| consul monitor                            | agent_prefix "": policy = "read"                                      |
| consul leave                              | agent_prefix "": policy = "write"                                     |   
| consul members                            | node_prefix "": policy = "read"                                       | 
| consul acl                                | acl = "write"                                                         |
| consul catalog services                   | service_prefix "": policy = "read"                                    |
| consul catalog nodes                      | node_prefix "": policy = "read"                                       | 
| consul services register                  | service_prefix "": policy = "write"                                   |                             |
| consul services register (Connect proxy)  | service_prefix "": policy = "write", node_prefix "": policy = "read"  |
| consul connect intention                  | service_prefix "": intention = "write"                                |
| consul kv get	                            | key_prefix "": policy = "read"                                        |
| consul kv put                             | key_prefix "": policy = "write"                                       |

# One Meshy B****

What Version of Envoy can I use?
https://www.consul.io/docs/connect/proxies/envoy#supported-versions



# What do you need in production?
https://learn.hashicorp.com/tutorials/consul/service-mesh-production-checklist?in=consul/developer-mesh



client 

consul acl token create -token $TOKEN \
  -description "ConsulServer agent token" \
  -policy-name ConsulServer | tee server.token

consul acl set-agent-token -token $TOKEN agent $(cat server.token  | grep SecretID  | awk '{print $2}')

create policy
consul acl policy create -token-file /root/myToken.token \
  -name consul-client \
  -rules @/consul/config/client_policy.hcl

create token with policy  
consul acl token create -token-file /root/myToken.token \
  -description "consul-client agent token" \
  -policy-name consul-client | tee client.token
 
Tokens for Consul Connect service mesh
If you are using a sidecar proxy as part of Consul Connect, it will inherit the token from the service definition. Alternatively, 
if you are deploying a proxy with a stand-alone registration file you will need to create a separate token. 
You will need to provide write privileges for the service and proxy, and read privileges for the service_prefix and node_prefix.



# 18hrs of videos


consul notes

virtual private cloud
public subnet
	load balancer points to consul server so we can see ui
private subnet
	server and clients are on different subnets

bind address
is for any internal cluster communications

client address
when you want to access via ui, anything inbound i.e. human to api

advertise address 
I'm of this ip address, want to point clients to a different address than the bind or LB


systemd resolve --status

remove configured ip tables
iptables -t nat -F

download 
curl -LO https://github.com/nicholasjackson/fake-service/releases/download/v0.23.1/fake_service_linux_amd64.zip

copy from windows to linux box
curl -LO https://github.com/nicholasjackson/fake-service/releases/download/v0.23.1/fake_service_linux_amd64.zip
unzip 

add executable to fiel
sudo chmod +x fake-service

move to bind
sudo mv fake-service /usr/local/bin

fake service unit file
/etc/systemd/system/api.service

[Unit]
Description=API
After=syslog.target network.target

[Service]
Environment="Message=friendly api message"
Environment="Name=api"
ExecStart=/usr/local/bin/fake-service
ExecStop=/bin/sleep 5
Restart=always

[Install]
WantedBy=multi-user.target


register with consul in /etc/consul.d/api.hcl

service {
  name = "api"
  port = "9090"
}


Web unit file
/etc/systemd/system/web.service

[Unit]
Description=web
After=syslog.target network.target
[Service]
Environment="MESSAGE=I AM WEB"
Environment="NAME=web"
Environment="UPSTREAM_URIS=http://api.service.consul:9090"
ExecStart=/usr/local/bin/fake-service
ExecStop=/bin/sleep 5
[Install]
WantedBy=multi-user.target


service {
  name = "web"
  port = "9090"
  
  check {
    id = "web"
    name = "HTTP Web on Port 9090"
    http = "http://localhost:9090/health"
    interval = "30s"
  }
}


remove Service from consul
consul services deregister -id=counting-1

# create one for the api service
consul acl token create -service-identity="counting-1:dc1"

consul acl token create -service-identity="api:dc1"
consul acl token create -service-identity="web:dc1"
# Fake Service Systemd Unit File
cat > /etc/systemd/system/api.service <<- EOF
[Unit]
Description=API
After=syslog.target network.target
[Service]
Environment="MESSAGE=api"
Environment="NAME=api"
ExecStart=/usr/local/bin/fake-service
ExecStop=/bin/sleep 5
Restart=always
[Install]
WantedBy=multi-user.target
EOF

# Reload unit files and start the API
systemctl daemon-reload
systemctl start api

# Consul Config file for our fake API service
cat > /etc/consul.d/api.hcl <<- EOF
service {
  name = "api"
  port = 9090
  token = "" # put api service token here
  check {
    id = "api"
    name = "HTTP API on Port 9090"
    http = "http://localhost:9090/health"
    interval = "30s"
  }
  connect {
    sidecar_service {
      port = 20000
      check {
        name     = "Connect Envoy Sidecar"
        tcp      = "127.0.0.1:20000"
        interval = "10s"
      }
    }
  }
}
EOF

systemctl restart consul

cat > /etc/systemd/system/consul-envoy.service <<- EOF
[Unit]
Description=Consul Envoy
After=syslog.target network.target
# Put api service token here for the -token option!
[Service]
ExecStart=/usr/bin/consul connect envoy -sidecar-for=api -envoy-version=1.20.0 -token=api_service_token
ExecStop=/bin/sleep 5
Restart=always
[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start consul-envoy


curl --silent \
       --header "X-Consul-Token: $CONSUL_HTTP_TOKEN" \
       127.0.0.1:8500/v1/agent/self | jq .DebugConfig.ACLDefaultPolicy


curl -s -H "Application/json" -H "CONSUL_HTTP_TOKEN:b79b3a9b-6991-65d7-a029-8c993dedcc63" http://127.0.0.1:8500/v1/agent/self | jq -r .xDS


# create one for the web service
consul acl token create -service-identity="web:dc1"


cat > /etc/consul.d/web.hcl <<- EOF
service {
  name = "web"
  port = 9090
  token = "" # put api service token here
  check {
    id = "web"
    name = "HTTP Web on Port 9090"
    http = "http://localhost:9090/health"
    interval = "30s"
  }
  connect {
    sidecar_service {
      port = 20000
      check {
        name     = "Connect Envoy Sidecar"
        tcp      = "127.0.0.1:20000"
        interval = "10s"
      }
      proxy {
        upstreams {
          destination_name   = "api"
          local_bind_address = "127.0.0.1"
          local_bind_port    = 9091
        }
      }
    }
  }
}
EOF


systemctl restart consul

cat > /etc/systemd/system/consul-envoy.service <<- EOF
[Unit]
Description=Consul Envoy
After=syslog.target network.target
# Put web service token here for the -token option!
[Service]
ExecStart=/usr/bin/consul connect envoy -sidecar-for=web -token=web_service_token
ExecStop=/bin/sleep 5
Restart=always
[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start consul-envoy




don't forget to staple certs in the together
consul connect envoy \
       -grpc-addr=https://127.0.0.1:8502 \
       -ca-file=/etc/consul.d/ssl.chain.pem \ <----- this must be INTERMEDIATE/ROOT in same file, in that order; you can use `-ca-path` but it's the same deal `/etc/consul.d/ssl.ca.d/ssl.chain.pem` with INTERMEDIATE/ROOT in *SINGLE* file
       -client-cert=/etc/consul.d/ssl.crt.pem \ <---- only the client cert, or it will fuck up
       -client-key=/etc/consul.d/ssl.key.pem \
       -http-addr=https://127.0.0.1:8501 \
       -tls-server-name=server.dc1.consul \
       -token=...gateway_token... \
       -admin-bind 127.0.0.1:19005 \
       -envoy-version=1.14.2 \
       -gateway=mesh \
       -register \
       -address "...lan...:8080" \
       -wan-address "...wan...:8080"\
       -service "gateway-primary"
