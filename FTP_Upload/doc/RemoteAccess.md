# Remote Access
The FTP_Upload package comes with a mechanism to allow remote access to the upload machine even though it may behind a NAT firewall.

Currently, this package contains a Linux shell script to access the upload machine from another Linux machine.  A Windows batch-file version has been prototyped and is expected to be available in the near future.

## Setting Up Remote Access from Linux
We'll call the machine that you're going to use to access the upload machine the "client" machine.

The remote access mechanism uses SSH (Secure Shell), so your Linux client machine must have OpenSSH installed.

Copy the file `starttunnel.sh` from the `FTP_Upload/tunnel` directory to someplace convenient on your Linux client machine.  Run an editor on the file, and near the top of the file, in the Configuration Section, change the `ACCT=myaccount@myhost.com` line to substitute the account on the cloud server that you are using to upload image files.  For example, if your cloud server is called "myneighorhood.org" and the user name is "camera", you would change the line to read

    ACCT=camera@myneighborhood.org
    
After you have made this change, make sure the file has execute permissions and move move the `starttunnel.sh` file into a directory in your execution path, such as the `bin` directory under your home directory, and change its name to `starttunnel`.  For example,

    chmod +x starttunnel.sh
    mv starttunel.sh $HOME/bin/starttunnel

The `starttunnel` script will give you SSH command-line access to the upload machine. It will create a "tunnel" from your client machine, through the cloud server to the upload machine. On the client machine, the tunnel will terminate in a TCP port that you select.  Once the tunnel is created, you can connect your SSH client to the selected TCP port in order to get command line access to the upload machine.  You can pick any port number between 1025 and 49151.

## Accessing the Upload Machine Using `starttunnel`

The syntax for the starttunnel command is,

>
>starttunnel *upload_machine_name* *port_number*
>

The name of the upload machine is the name you specified during the FTP_Upload installation process.  So, if the name of the upload machine is "carnaby," and you want to use port 22222 on your local client machine, you would give the command,

    starttunnel carnaby 22222

If you do not have an SSH key pair set up between your client machine and the server (handy, but not required), you must enter the password of the uploading account on the cloud server (camera@myneighborhood.org in our example) when asked.

After a few seconds (up to about 20), `starttunnel` should print the message, `Tunnel ready...` and exit.  You can then connect your SSH client to port 22222 and log in to the upload machine.

Let's assume the user name for the account on the upload machine you would like to connect to is "fred." Once you have seen the `Tunnel ready...` message, give the command:

    ssh fred@localhost -p 22222

(You need tell SSH that the machine name is `localhost` because you're asking to connect to a port on the local client machine.) At this point, if you have not connected to this uploader machine on this port before, you will receive a message saying,

>The authenticity of host '[localhost]:22222 ([127.0.0.1]:22222)' can't be established.
>ECDSA key fingerprint is ...
>Are you sure you want to continue connecting (yes/no)?

Answer "yes".  

Then, enter the password for the "fred" account on the upload machine, and you should see the login message and command line prompt from the upload machine.

When done, type `exit` to logout and close the tunnel connection.



