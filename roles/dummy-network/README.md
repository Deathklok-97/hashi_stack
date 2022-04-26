
https://zendesk.engineering/making-docker-and-consul-get-along-5fceda1d52b9


put this there  | 
                v
# /etc/environment
CONSUL_HTTP_ADDR=169.254.1.1:8500
CONSUL_RPC_ADDR=169.254.1.1:8400


Why?

# Ideas we considered, but rejected

## Configuring Consul to bind to all interfaces. That would make the HTTP and CLI RPC ports open to the world unless we also craft iptables(8) rules to block requests from foreign hosts. In addition, we’d have to ensure the containers know the IP address of the host they’re running on in order to communicate with its Consul agent.

## Configuring Consul to bind to the Docker bridge IP address. The routing would work properly, but: (a) typically, bridge interfaces are assigned dynamically by Docker; (b) there may be more than one bridge interface; (c) containers would have to know the IP address of the selected bridge interface; and (d) the Consul agent and dnsmasq (discussed below) would not be able to start until the Docker engine has started. We don’t want to create any unnecessary dependencies.

## Installing a Consul agent per container. Consul’s architecture anticipates a single agent per host IP address; and in most environments, a Docker host has a single network-accessible IP address. Running more than one Consul agent per container would cause multiple agents to join the Consul network and claim responsibility for the host, causing major instability in the cluster.

## Sharing the Consul agent container’s network with application containers. A container can have exactly one network namespace. So, if your application containers share the network namespace with the Consul agent’s container, they will end up sharing network namespaces with each other as well. This would deprive us the benefits of network isolation that is a prime benefit of using containers in the first place.

