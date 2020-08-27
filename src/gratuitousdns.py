import pytz
import socket
import hashlib
import datetime
import argparse

from dnslib import TXT, A, AAAA, RR
from dnslib.server import DNSLogger, DNSServer, RR, QTYPE, RCODE

class GratuitousDnsServer:
	def __init__(self, resolver, logger):
		self.resolver = resolver
		self.logger = logger
	
	def run(self, bindAddr, blocking):
		server = DNSServer(self.resolver, port=53, address=bindAddr, logger=self.logger)

		if blocking:
			server.start()
		else:
			server.start_thread()

class GratuitousResolver:
	def __init__(self):
		pass
	
	def resolve(self, request, handler):
		reply = request.reply()
		
		# DNSLabel qname
		qname = request.q.qname

		if qname.matchSuffix("time.") or qname.matchSuffix("date."):
			utc_now = pytz.utc.localize(datetime.datetime.utcnow())
			try:
				timezone = str(qname)[:-6].replace('.', '/')
				tz_now = utc_now.astimezone(pytz.timezone(timezone))
			except pytz.UnknownTimeZoneError:
				reply.header.rcode = RCODE.REFUSED
				return reply
			
			if qname.matchSuffix("time."):
				reply.add_answer(RR(qname, QTYPE.A, ttl=0, rdata=A(tz_now.strftime("%H.%M.%S.0"))))
			elif qname.matchSuffix("date."):
				reply.add_answer(RR(qname, QTYPE.A, ttl=0, rdata=A(tz_now.strftime("%y.%m.%d.0"))))
				
			reply.add_answer(RR(qname, QTYPE.TXT, ttl=0, rdata=TXT(tz_now.strftime("%Y-%m-%d %H:%M:%S"))))
			reply.add_answer(RR(qname, QTYPE.AAAA, ttl=0, rdata=AAAA(tz_now.strftime("%Y:%m:%d::%H:%M:%S"))))
		
		elif qname.matchSuffix("md5."):
			md5 = hashlib.md5(str(qname.stripSuffix("md5."))[:-1])
			hash = str(md5.hexdigest())
			ipv6 = ':'.join([hash[i:i+4] for i in range(0, len(hash), 4)])
			reply.add_answer(RR(qname, QTYPE.AAAA, ttl=0, rdata=AAAA(ipv6)))
			reply.add_answer(RR(qname, QTYPE.TXT, ttl=0, rdata=TXT(hash)))
		
		if RR() == reply.get_a():
			reply.header.rcode = RCODE.NXDOMAIN
		return reply

if __name__ == '__main__':
    # shell args
    p = argparse.ArgumentParser(description="Gratuitous DNS server")
    p.add_argument("--bind", "-b",
                   default="127.0.0.1",
                   metavar="<interface address>",
                   help="Listen address (default: 127.0.0.1)")
    p.add_argument("--log",
                   default="request,reply,truncated,error",
                   help="Log hooks to enable (default: +request,+reply,+truncated,+error,-recv,-send,-data)")
    args = p.parse_args()
    
    resolver = GratuitousResolver()
    logger = DNSLogger(args.log)
    server = GratuitousDnsServer(resolver, logger)
    
    print "Starting server - press ^C to quit..."
    server.run(args.bind, True)

