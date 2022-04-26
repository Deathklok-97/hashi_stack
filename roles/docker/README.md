Have Networking allow 


https://registry-1.docker.io/v2/
301'd to 

 download.docker.com
 auth.docker.io
 index.docker.io
 production.cloudflare.docker.com
 mcr.microsoft.com
 centralus.data.mcr.microsoft.com


Installing Docker
---

Docker install

sudo apt-get update

sudo apt-get install \
   ca-certificates \
   curl \
   gnupg \
   lsb-release

Add gpg key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

setup stable repo
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

install ce
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

sudo docker run hello-world


<!--  install at location /etc/docker file named daemon.json with contents
 {
   "icc": false,
   "tls": true,
   "tlsverify": true,
   "tlscacert": "/etc/docker/ssl/ca.pem",
   "tlscert": "/etc/docker/ssl/server.pem",
   "tlskey": "/etc/docker/ssl/serverkey.pem",
   "userland-proxy": false,
   "default-ulimit": "nofile=50:100",
   "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2376"],
   "insecure-registries": ["p-dockerrepo.tpgi.us:5000"]
 } -->

Unit file for docker. Removed exec start with 2375 meaning unsecured
install in this location /lib/systemd/system/docker.service

[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network-online.target firewalld.service containerd.service
Wants=network-online.target
Requires=docker.socket containerd.service

[Service]
Type=notify
 the default is not to use systemd for cgroups because the delegate issues still
 exists and systemd currently does not support the cgroup feature set required
 for containers run by docker
ExecStart=/usr/bin/dockerd
ExecReload=/bin/kill -s HUP $MAINPID
TimeoutSec=0
RestartSec=2
Restart=always

Note that StartLimit* options were moved from "Service" to "Unit" in systemd 229.
Both the old, and new location are accepted by systemd 229 and up, so using the old location
to make them work for either version of systemd.
StartLimitBurst=3

Note that StartLimitInterval was renamed to StartLimitIntervalSec in systemd 230.
Both the old, and new name are accepted by systemd 230 and up, so using the old name to make
this option work for either version of systemd.
StartLimitInterval=60s

Having non-zero Limit*s causes performance problems due to accounting overhead
in the kernel. We recommend using cgroups to do container-local accounting.
 LimitNOFILE=infinity
 LimitNPROC=infinity
 LimitCORE=infinity

  Comment TasksMax if your systemd version does not support it.
  Only systemd 226 and above support this option.
 TasksMax=infinity

  set delegate yes so that systemd does not reset the cgroups of docker containers
 Delegate=yes

  kill only the docker process, not all processes in the cgroup
 KillMode=process
 OOMScoreAdjust=-500

 [Install]
 WantedBy=multi-user.target

Get them certs 
 chmod -v 0400 ca-key.pem key.pem server-key.pem

 prevent accidental damage 
 chmod -v 0444 ca.pem server-cert.pem cert.pem

 make dir then -> where to store them 
/etc/docker/ssl

 dockerd \
     --tlsverify \
     --tlscacert=ca.pem \
     --tlscert=server-cert.pem \
     --tlskey=server-key.pem \
     -H=0.0.0.0:2376

 Secure by default
 If you want to secure your Docker client connections by default, 
 you can move the files to the .docker directory in your home directory --- 
 and set the DOCKER_HOST and DOCKER_TLS_VERIFY variables as well (instead of passing -H=tcp://$HOST:2376 and --tlsverify on every call).

  mkdir -pv ~/.docker
  cp -v {ca,cert,key}.pem ~/.docker
  
export DOCKER_HOST=tcp://$HOST:2376 DOCKER_TLS_VERIFY=1

 
installed correctly test
 
sudo docker run hello-world



 Uninstall docker

 sudo apt-get purge -y docker-engine docker docker.io docker-ce docker-ce-cli
 sudo apt-get autoremove -y --purge docker-engine docker docker.io docker-ce  

 sudo rm -rf /var/lib/docker /etc/docker
 sudo rm /etc/apparmor.d/docker
 sudo deluser docker
 sudo groupdel docker
 sudo rm -rf /var/run/docker.sock



# p-searchfeed
10.15.30.81

dockerd --debug \
   --tls=true \
   --tlscert=/server/server.pem \
   --tlskey=/server/serverkey.pem \
   --host tcp://10.15.30.81:2376
   
{
  "debug": true,
  "tls": true,
  "tlscert": "/var/docker/server.pem",
  "tlskey": "/var/docker/serverkey.pem",
  "hosts": ["tcp://10.15.30.81:2376"]
}

docker context create \
    --docker host=ssh://docker-user@host1.example.com \
    --description="Remote engine" \
    my-remote-engine
		
openssl req -new -x509 -days 365 -key ca-key.pem -sha256 -out ca.pem

openssl req -subj "/CN=10.15.30.81" -sha256 -new -key server-key.pem -out server.csr
echo subjectAltName = DNS:p-searchfeed,IP:10.15.30.81,IP:127.0.0.1 >> extfile.cnf

docker context create prod-engine --description "p-searchfeed" --docker "host=tcp://p-searchfeed:2376,ca=~/.certs/ca.pem,cert=~/.certs/cert.pem,key=~/.certs/key.pem"





docker fight 

create directory that will hold CA cert/key client cert/key
sudo su - 
mkdir -p /docker/apps/ssl 
chmod 700 /docker/apps/ssl


Create CA private key and cert
openssl genrsa -out /docker/apps/ssl/ca-key.pem 4096
openssl req -x509 -new -nodes -key /docker/apps/ssl/ca-key.pem -days 3650 -out /docker/apps/ssl/ca.pem -subj '/CN=docker-CA'

Create open ssl.cnf to be used by CA
vi /docker/apps/ssl/openssl.cnf 
[added]

    [req]
    req_extensions = v3_req
    distinguished_name = req_distinguished_name
    [req_distinguished_name]
    [ v3_req]
    basicConstraints = CA:FALSE
    keyUsage = nonRepudiation, digitalSignature, keyEncipherment
    extendedKeyUsage = serverAuth, clientAuth


# Create Client TLS cert
openssl genrsa -out /docker/apps/ssl/client-key.pem 4096
openssl req -new -key /docker/apps/ssl/client-key.pem -out /docker/apps/ssl/client-cert.csr -subj '/CN=docker-client' -config /docker/apps/ssl/openssl.cnf
openssl x509 -req -in /docker/apps/ssl/client-cert.csr -CA /docker/apps/ssl/ca.pem -CAkey /docker/apps/ssl/ca-key.pem -CAcreateserial -out /docker/apps/ssl/client-cert.pem -days 3650 -extensions v3_req -extfile /docker/apps/ssl/openssl.cnf
