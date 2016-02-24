# SYN Flood Prevention using iptables against Scapy SYN packets generated
> /tmp/DDOS_IP.log
> /tmp/test1.txt
> /tmp/test2.txt
trap "echo ;echo Caught EXIT signal;iptables -F;echo Iptables entries cleared;echo HaX0R SVP" EXIT
while true;
do
date >> /tmp/DDOS_IP.log
netstat | grep -E "ssh|www" | grep -iv ESTABLISHED | awk '{print $5}' | cut -d : -f 1 | sort | uniq -c >> /tmp/DDOS_IP.log
for pip in `netstat | grep -E "ssh|www" | grep -iv ESTABLISHED | awk '{print $5}' | cut -d : -f 1 | sort | uniq`
do
conntrack=`netstat | grep -E "ssh|www" | grep -iv ESTABLISHED | awk '{print $5}' | cut -d : -f 1 | grep $pip | wc -l`;
while read line
do
if [ "$line" = "$pip" ]
then
continue 2
fi
done < /tmp/test2.txt
if [ "$conntrack" -gt "25" ]
then
iptables -I INPUT -s $pip -p tcp -j REJECT --reject-with tcp-reset
echo "$pip" >> /tmp/test1.txt
fi
done
cat /tmp/test1.txt | sort | uniq > /tmp/test2.txt
sleep $1
done
