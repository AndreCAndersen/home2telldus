# home2telldus
Integration between Google Home and Telldus Live

Because Telldus Live (as of February 4th 2020) no longer supports IFTTT, 
I'm building this interface  in order to still be able to give Google Home 
commands to my devices connected to Telldus Live.

If I don't make this tool, all the devices I have bought for Telldus Live
will be useless.

Development plan:

1. Build basic Telldus client interface: Done.
2. Build basic Google Home interface: Pending
3. Integrate Google Home and Telldus Live: Pending

Usage:

To run a Telldus command run the `Home2TelldusCli` command line interface.
Do one of the following:

1) Set the environment variables: `TELLDUS_EMAIL` and `TELLDUS_PASSWORD` and 
run your command:

```
python3 main.py run --device_name="My Lamp" --command=on
```

2) ... or just set the email and password in the command line as well:

```
python3 main.py run --device_name="My Lamp" --command=on --email=hello@example.com --password=SECRET
```
