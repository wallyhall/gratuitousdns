# gratuitousdns
A DNS server which does things DNS wasn't meant to do.  Just because we can.

## Required packages

```
pip install pytz
pip install dnslib
```

## Usage

Easy!

```
py gratuitousdns.py --bind 127.0.0.1 --log request
```

Then query it:

```
nslookup helloworld.md5 127.0.0.1
nslookup europe.london.time 127.0.0.1
nslookup europe.paris.date 127.0.0.1
```
