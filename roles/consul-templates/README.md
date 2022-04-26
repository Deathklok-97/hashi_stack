Rotate Gossip Key
Consul provides a command, consul keyring that helps manage keys in the datacenter. Issue the command below to see what key is in effect.
consul keyring -list


To rotate the key we need to use the consul keyring -install "<new_gossip_key>" command. 
Go ahead and issue the command below to install the new gossip key. 
This will propagate the key to all nodes in the datacenter automatically.
NEW_GOSSIP_KEY=$(cat /opt/consul/gossip/gossip.key) && consul keyring -install $NEW_GOSSIP_KEY


promote the new gossip key as the primary.
consul keyring -use $NEW_GOSSIP_KEY

ou should remove all the former keys, to avoid nodes being able to join the gossip pool with an old key. 
You can remove the old key by using the consul keyring -remove "<old_gossip_key"
consul keyring -remove "KB1IvPR2sc7LIsDbgJkeCmj05oNsrTEf40FWedRFujE="


Automate gossip key rotation


This lab contains an example script, /opt/consul/templates/rotate_key.sh that you can use for this. You may review the script by visiting the Editor tab.
killall -9 consul-template



Start consul-template with new configuration
consul-template --vault-addr $VAULT_ADDR -config "/opt/consul/templates/consul_template_autorotate.hcl" 2>&1 &


Now every time you update the key value in Vault, consul-template will make sure that the key is installed in Consul too.
create a new gossip key.
vault kv put kv-v2/consul/config/encryption key=$(consul keygen) ttl=11s


After 20 seconds the script will pick up the gossip.key file containing the new key and use it to rotate the Consul gossip encryption key. It should output the following lines
==> Installing new gossip encryption key...
==> Changing primary gossip encryption key...
==> Removing gossip encryption key...


test the key is actually changed in Consul using again the consul keyring command.
consul keyring -list









First, enable key/value v2 secrets engine (kv-v2).
vault secrets enable kv-v2

Once the secret engine is enabled, verify it this using the following command:
vault secrets list

The consul binary can be used to generate a valid gossip encryption key by using the keygen command.
export CONSUL_GOSSIP_KEY=$(consul keygen)

Write encryption key in Vault
vault kv put kv-v2/consul/config/encryption key=${CONSUL_GOSSIP_KEY} ttl=10s



Integrate consul-template with Vault
Once the key is stored in Vault, you can retrieve it from any machine that has access to Vault.

From your Consul server node, use the vault kv get command using the -field parameter to retrieve the key value only.

vault kv get -field=key kv-v2/consul/config/encryption | tee /encryption.key



consul-template
You can use consul-template in your Consul datacenter to integrate with Vault's KV Secrets Engine to dynamically rotate you Consul gossip encryption keys.

This lab will demonstrate the gossip encryption rotation so that you can deploy a Consul datacenter that will automatically rotate the gossip encryption key based on updates in Vault. You will use consul-template that can render the actual certificates and keys on the nodes in your cluster. The consul-templates are located in /opt/consul/templates/.

Go to the Editor Tab to view the consul template files.

Start consul-template
To start consul-template you must provide the file with the -config parameter.

consul-template --vault-addr $VAULT_ADDR -config "/opt/consul/templates/consul_template.hcl" 2>&1 &

view file
cat /opt/consul/gossip/gossip.key

example output
5EyLRD8B27B7kN+T547GDnj9dmABCyRvSvrPSw56rL0=

consul-template will automatically update the file every time the key is updated in Vault. You can test this by generating a new key:
vault kv put kv-v2/consul/config/encryption key=$(consul keygen) ttl=10s

If the key is not updated, wait for 30 seconds and then read the gossip.key file again.
cat /opt/consul/gossip/gossip.key