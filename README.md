Web Team's environment notes/scripts

$ ap -i ./inventory -u ansible -v playbook.yml<br>

# Playbooks

**Ansible**
[basics](https://linuxhint.com/install_ansible_ubuntu/)

<strong>_Pitcher:_</strong> </br>

<ol>
<li><div>Update</div><div>sudo apt update</div></li>
<li><div>Focal is shipped with ansible</div><div>sudo apt install ansible</div></li>
<li><div>Are we installed???</div><div>ansible --version</div></li>
<li><div>Generate ssh key</div><div>ssh-keygen</div></li>
</ol>

<strong>_Catcher:_</strong> </br>

<ol>
<li><div>Update</div><div>sudo apt update</div></li>
<li><div>Install openssh-server</div><div>sudo apt install openssh-server -y</div></li>
<li><div>Start on startup</div><div>sudo systemctl status sshd</div></li>
<li><div>Firewall to allow SSH access</div><div>sudo ufw allow ssh</div></li>
<li>
<div>
<strong>The above is probably already done </strong>
</div>
</li>
<li>
<div> Goal: Create an ansible user and allow password-less sudo access</div>
<div>sudo adduser ansible</div>
<div>hit enter a lot and then y</div>
</li>
<li>
<div>Configure password-less sudo access to the ansible user</div>
<div>echo "ansible ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ansible</div>
<li><div>Get Catcher IP Address</div><div>hostname -I</div><div>##will output {{some-ip-address}} </div></li>
<li><div>Go to Pitcher </div><div>ssh-copy-id ansible@{{some-ip-address}}</div><div>Type yes then press Enter key</div></li>
<li><div>Go back to Catcher <Enter></div></li>
<li><div>Disable password-based login for the ansible user</div><div>sudo usermod -L ansible</div></li>
<li><div>Go to Pitcher <Enter></div></li>
<li><div>Pitch into Catcher</div><div>ssh ansible@{{some-ip-address}}</div></li>
</ol>

<strong>_ETC_</strong></br>

if you want to allow password-based login for the ansible user again (Why?)</br>
Run from catcher sudo usermod -U ansible </br>

sshd not active?</br>
sudo systemctl start sshd </br>

sshd not enabled? (not added to the system startup) </br>
sudo systemctl enable sshd </br>

<h2> Tests </h2>
<ul>
<li>
    mkdir ~/ansible-demo
</li>
<li>
    cd ~/ansible-demo/
</li>
<li>
    nano hosts </br>
    {{some-ip-address}} </br>
</li>
<li>
    ansible all -i ./inventory -u ansible -m ping
</li>
<li>
ansible all -i ./inventory -u ansible -m shell -a 'echo "$(hostname) - $(hostname -I)"'
</li>
</ul>

<h2> Aliases </h2>
<ul>
<li> alias ap='ansible-playbook'</li>
<li> alias acl='ansible-config list'</li>
<li> alias ail='ansible-inventory --list'</li>
</ul>




# General Linux Notes
Udemy Linux notes

"tail" -15 /var/log/auth.log 
head
cat
tail

cd ~ - go to home directory

pwd 	- print working directory
ls -alh - all files list readable form
ll -h	- alias 

add an alias 
nano ~/.bash_aliases

example aliases below

# playbook
alias ap='ansible-playbook'

#config
alias acl='ansible-config list'

#inventory
alias ail='ansible-inventory --list'


find - find files
sudo updatedb
locate auth

grep
sudo grep opened /var/log/auth.log -find logged in users
sudo cat /var/log/auth.log | more  (U to go up D to go down)
sudo cat /var/log/auth.log | less  (arrow key movement)

ls /var - relative path
mkdir var - make directory named var

ls /var - is at root
ls /home/clwilson@TPGI.US/var (absolute path)

cp - copy files args (filename, end destination)

use useradd over adduser
it's more universal

commonly used options 
-d (home directory)
-m (create hom dir)

sudo useradd -d /home/dtrump -m dtrump 

- set user password
sudo passwd dtrump
KendallSucks

adduser is a perl script (Does more for you)
sudo adduser lskywalker 
Both made a group for us

list all users (multiple ways)
ls /home 

What group is a user assigned to 
cat /etc/group | grep <user>

sudo usermod -aG sudo lskywalker (give sudo by adding to sudo group)


#Remove from group
sudo gpasswd -d root elasticsearch

gpasswd -d user group

# or
usermod -R group user_name



sudo usermod -L dtrump (Lock an account)
sudo usermod -U dtrump (Unlock an account)

man vipw (edit shadow file (very bad practice))
sudo vipw 
sudo vipw -s
escape+ :q! to get out without saving

man userdel
userdel -> recommends using deluser instead

rwx -> executable
-|rw-|rw-|r-- cwilson cwilson

1 - indicates file type dir, reg file, symbolic link, etc.
2 next 3 chars rw- are the permissions the user who created or owns the file
3 the next three rw- again are for group that is assigned to the file. This group means it has read write access
4 The third three characters, r-- are for all other users, so they can read but not write to the file 

One user that owns the file 
group that owns the file

Set Primary Group for User
sudo usermode -g <group> <user>

--remove-home --remove-all-files

Common places to keep things create directories 
/var/share
/var/local/share
/home/share
/share
/srv
Anyplace that makes sense to you

sudo addgroup rebel-alliance
sudo chgrp rebel-alliance /home/rebel-alliance/

Add a user to a group
sudo usermod -aG rebel-alliance lskywalker


refresh groups
exec su -l $USER
or 
newgrp docker

Add permissions to write to folder
sudo chmod g+rwx /home/rebel-alliance/

Remove read permissions will remove outside group
chmod o-r [filename]

Change ownership of folder recursively
sudo chown -R username:group directory

I messed up opt, what's the default
sudo chown root:root /opt
sudo chmod 0755 /opt

nano text editor

M is alt
^ is cmd

SIMPLE VERSIONING 
make a back up 
cp sshd sshd.0

change file
nano sshd 
look at diff
diff sshd sshd.0

make a copy
cp sshd sshd.1
move altered into original
mv sshd.0 sshd

ls

File structure 
man hier 
https://www.pathname.com/fhs/

(wget is non interactive)
sudo wget https://downloads.cisofy.com/lynis/lynis-3.0.1.tar.gz 
https://nodejs.org/dist/v14.15.1/node-v14.15.1.tar.gz
unzip it 
sudo tar -zxvf lynis/lynis-3.0.1.tar.gz\

changing permissions on a file can be set to user/group/others
permissions can be given: read write execute
using the chmod command

make no one able to read to allow change - to +
chmod o-r test.txt //other
chmod u-r test.txt //user
chmod g-r test.txt //group
 
= will override permissions with the ones specified

//all
chmod a-r test.text // no one can read it

permission are numeric as well 
soooooo
r | w | x
4 | 2 | 1

rwx = 4+2+1 = 7
r-- 4+0+0 = 4

chmod 755 does the same as 
chmod u=rwx <filename>
chomd go=rx <filename>

Hiddle files
put a period in the from of it 
touch .HiddenFile

works the same with directories 
How do I see it? 
ls -a will show them 

Copying Deleting Renaming files

cp [file to copy] [new name of file]
man cp

copy everything 
cp * [directory] 
including directory
cp -r [old dir] [new dir]

remove everything 
rm *
remove one 
rm [filename]
remove directory and any subdirectorys
rm -rf [directory name] //Doesn't remove securely

to securely delete 
man shred
shred -uv [filename]

to securely destroy directories 
sudo apt install wipe
man wipe
man -rfi [directory]

to move a file
mv command
mv [filename] [destination]

mv is used to rename file
mv test.txt test1.txt
just renamed test to test1 

rename directory
mv /home/user/old_dir_name /home/user/new_dir_name

move contents up one directory
mv subfolder/* subfolder/.


Linking to files
soft or hard links (Shortcut in Windows)
Inode numbers are how the system tracks files
ls -li to see inode numbers
df -i to see how many inodes are used 

Huge info 
sudo tune2fs -l [filesystem] | grep -i inode

soft link to filename
ln -s [softlinkname] [filename]
hard link is to inode number

soft links will show red when busted

find dump errors into bitbucket with the (redirect errors to devnull) 2> devnull
find / -name "[filename]*" 2> devnull

get number of lines 
 | wc -l
word count and how many lines match

search by file type
f files
l links
s sockets
d directories


WHAT AM I USING 
cat /etc/*-release
 
UPGRADE EVERYTHING 
sudo apt-get update && sudo apt-get upgrade && sudo apt-get dist-upgrade

WHAT IS MY IP
ip addr | grep inet
or
Hostname -I

notes 

copy my box to linux box recursively
pscp -P 22 -r C:\Users\clwilson\source\repos\js-simple-api\_dist\ clwilson@TPGI.us@10.123.13.179:/var/www/api/

copy my box to linux box
pscp -P 22 -r c:\Users\clwilson\Downloads\dump.rdb clwilson@TPGI.us@10.123.13.183:/var/lib/redis

copy linux to my box
pscp clwilson@10.123.13.181:/etc/consul/tls/certificate.pfx C:\Users\clwilson\Downloads


wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.0/install.sh | bash

nginx 
https://nginx.org/packages/ubuntu/ focal nginx

jq lightweight flexible command-line json processor
sudo apt install jq -y

pipe through jq '| jq'
 
Who's in jail???
sudo iptables -n -L

Scout the Prison
make fail2ban file below to get jail
#!/bin/bash

JAILS=`fail2ban-client status | grep "Jail list" | sed -E 's/^[^:]+:[ \t]+//' | sed 's/,//g'`
for JAIL in $JAILS
do
  fail2ban-client status $JAIL
done

make executable
chmod +x script-name-here.sh

run your script, enter:
./script-name-here.sh


JailBreak
sudo fail2ban-client set sshd unbanip 10.131.9.128

Move up one directory
mv folder/* .

change permissions
/var/lib/apm-server/meta.json

Who owns pid
ps -o user= -p PIDHERE

Increase Inotifywatches
sudo sysctl -w fs.inotify.max_user_watches=50000

configure sudo to never ask for you password/passwd
sudo visudo

Check space: 
free -m

Disable swap: 
swapoff -a

Wait approx 30 sec 
(use free -m to see the amount of swap used/available decrease over time)

Enable swap: 
swapon -a

How to check if port is in use on Linux or Unix
netstat -tulpn | grep LISTEN
ss -tulwn | grep LISTEN

Is WAN encrypted 
tcpdump 'udp port 4648' -A
