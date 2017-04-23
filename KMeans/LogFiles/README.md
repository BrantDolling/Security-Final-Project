# Log Files

 Sample log files used to initially test the FTPLogReader. Overfitting will likely be a huge problem for these log files. In the future, more robust log files will have to be created since these log files are rather small compared to those that would be generated in reality.
 
 Password guessing attacks were made from Kali Linux using hydra with the password list rockyou.txt. Due to time constraints, most attacks were stopped before they were successful. The exact command is:
  
~~~~

hydra -V 192.168.56.101 ftp -l test -P rockyou.txt

~~~~

where "user" was replaced by various users, both existant and nonexistant. Note that hydra will fail to tell you if the ip address is unreachable and will attempt to attack no matter what. Due to this, one must check that the ip address is reachable before the attack.

### Log Files

 - normal.log : Normal connections
 
 - attack.log : Connection attempts made by hydra.
 
 - mixed.log  : Both normal connections and attempts made by hydra. Created using the FTP fake traffic creator. IP addresses are stored in ips.txt
 
 
