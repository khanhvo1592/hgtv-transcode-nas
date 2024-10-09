## linux command
    sudo systemctl enable hgtv-transcode.service
    sudo systemctl start hgtv-transcode.service
## mount cifs - connect smb server
     sudo mount -t cifs //192.168.150.205/mobile /mnt/mobile -o credentials=/etc/smbcredentials,uid=1000,gid=1000,file_mode=0775,dir_mode=0775,vers=2.0
     sudo mount -t cifs //192.168.150.205/truyen_hinh/cho_duyet /mnt/cho_duyet -o credentials=/etc/smbcredentials,uid=1000,gid=1000,file_mode=0775,dir_mode=0775,vers=2.0