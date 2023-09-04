# Remote Access
The FTP_Upload package comes with a mechanism to allow remote access to the upload machine even though it may behind a NAT firewall.

Currently, this package contains a Linux shell script to access the upload machine from another Linux machine.  A Windows batch-file version has been prototyped and is expected to be available in the near future.

## Setting Up Remote Access from Linux
We'll call the machine that you're going to use to access the upload machine the "client" machine.

The remote access mechanism uses SSH (Secure Shell), so your Linux client machine must have OpenSSH installed.

Copy the file `starttunnel` from the `FTP_Upload/tunnel` directory to someplace convenient on your Linux client machine.
    
Make sure the file has execute permissions and move move the `starttunnel` file into a directory in your execution path, such as the `bin` directory under your home directory.  For example,

    chmod +x starttunnel
    mv starttunel $HOME/bin/starttunnel

You need to copy the private key file for the upload account on your cloud server to the file `$HOME/.ssh/id_rsa`.  If you have followed the [installation instructions](Installation.md) and run the installation script, this file will be on the upload machine under the maintenance account's home directory in the file `.ssh/id_rsa`.

The `starttunnel` script will give you SSH command-line access to the upload machine. It will create a "tunnel" from your client machine, through the cloud server to the upload machine. On the client machine, the tunnel will terminate in a TCP port that you select.  Once the tunnel is created, you can connect your SSH client to the selected TCP port in order to get command line access to the upload machine.  You can pick any port number between 1025 and 49151.

## Accessing the Upload Machine Using `starttunnel`

The syntax for the starttunnel command is,

>
>starttunnel *upload_machine_name* *port_number*
>

The name of the upload machine is the name you specified during the FTP_Upload installation process.  So, if the name of the upload machine is "carnaby," and you want to use port 22222 on your local client machine, you would give the command,

    starttunnel carnaby 22222

After a few seconds (up to about 20), `starttunnel` should print the message, `Tunnel ready...` and exit.  You can then connect your SSH client to port 22222 and log in to the upload machine.

For this example, we'll assume you want to log into the uploader's maintenance account, and that the account is named `maint`. Once you have seen the `Tunnel ready...` message, give the command:

    ssh maint@localhost -p 22222

(You need tell SSH that the machine name is `localhost` because you're asking to connect to a port on the local client machine.) At this point, if you have not connected to this uploader machine on this port before, you will receive a message saying something like,

>The authenticity of host '[localhost]:22222 ([127.0.0.1]:22222)' can't be established.
>ECDSA key fingerprint is ...
>Are you sure you want to continue connecting (yes/no)?

Answer "yes".  

Then, enter the password for the `maint` account on the upload machine, and you should see the login message and command line prompt from the upload machine.

When done, type `exit` to logout and close the tunnel connection.



