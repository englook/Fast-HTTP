from dataclasses import dataclass
import settings
from HTTPClient import HTTPClient

#PUBLIC_PROXIES_LIST

# Obtein os proxies
#client =  HTTPClient()
#response = client.get(settings.PUBLIC_PROX_RAW)

#print(response.content_text)

#proxies_raw = response.content_text.split('\n')
#print(proxies_raw)


PUBLIC_PROXIES_RAW = 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt'
PUBLIC_PROXIES_LIST = 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt'
PUBLIC_PROXIES_STATUS = 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-status.txt'

@dataclass
class ProxyParsed():
	proxy_ip                   : str
	proxy_port                 : int
	proxy_scheme               : str
	proxy_level_anonymity      : int
	proxy_country              : str
	proxy_google_passed        : bool
	proxy_outgoing_ip          : bool
	proxy_uri                  : str



class InvalidProxyToParser(Exception):
	pass


"""
	# Definitions

	1. IP address
	2. Port number
	3. Country code
	4. Anonymity
	   N = No anonymity
	   A = Anonymity
	   H = High anonymity
	5. Type
		 = HTTP
	   S = HTTP/HTTPS
	   ! = incoming IP different from outgoing IP
	6. Google passed
	   + = Yes
	   – = No
"""

import json

class ProxyListAPI():
	"""
	Uma lista de servidores proxy gratuitos, públicos e de encaminhamento.
	Disponibilizados diariamente em 'https://github.com/clarketm/proxy-list'.
	"""
	def __init__(self):
		self.client = HTTPClient()
		self._result = {}

	def get_proxy_list_raw(self):
		pass

	def get_proxy_list(self):
		pass

	def get_proxy_list_status(self):
		pass

	def proxy_ordenate(self, proxy_item, reference, name=None):
		if not reference in self._result:
			self._result[reference] = []
		else:
			self._result[reference].append(proxy_item.__dict__)

	def initialize(self):
		response = self.client.get(settings.PUBLIC_PROXY_LIST)
		proxies = response.content_text.split('\n\n')
		proxies_header = proxies[0]
		proxies_list = proxies[1].split('\n')
		self._result['info'] = {}
		for proxy_line in proxies_list:
			proxy_item = self.parse(proxy_line)
			# sort by schema type
			self.proxy_ordenate(proxy_item, f'scheme-{proxy_item.proxy_scheme}')
			# sort by anonymity level
			self.proxy_ordenate(proxy_item, f'level_anonymity-{proxy_item.proxy_level_anonymity}')
			# sort by country of origin
			self.proxy_ordenate(proxy_item, f'country-{proxy_item.proxy_country}')
			# sorts by http port
			self.proxy_ordenate(proxy_item, f'port-{proxy_item.proxy_port}')
			# sort by proxy who goes through google
			self.proxy_ordenate(proxy_item, f'google_passed-{proxy_item.proxy_google_passed}')
		self._result['info']['header'] = proxies_header
		self._result['info']['count_proxies'] = len(proxies_list)
		# Prepare a json file for cache
		with open('proxy-list-cache.json', 'w') as f:
			json.dump(self._result, f, indent=4)

	def parse(self, proxy_line):
		"""
		IP [1]
		|
		| Port [2]
		|   |
		|   | Country [3]
		|   |   |
		|   |   | Anonymity [4]
		|   |   |  |
		|   |   |  |  Type [5]
		|   |   |  |   |_ _ _ _
		|   |   |  |_ _ _ _ _  | Google passed [6]
		|   |   |_ _ _ _ _   | |  |
		|   |_ _ _ _ _    |  | |  |
		|             |   |  | |  |
		200.2.125.90:8080 AR-N-S! +
		└────────────┬────────────┘
				 Proxy line
		"""
		try:
			proxy_splited = proxy_line.split(' ')
			proxy_address_info = proxy_splited[0].split(':')
			proxy_ip = proxy_address_info[0]
			proxy_port = proxy_address_info[1]
			proxy_info = proxy_splited[1].split('-')
			proxy_country = proxy_info[0]
			proxy_level_anonymity = self._parse_anonymity(proxy_info[1])
			proxy_type = self._parse_proxy_type(proxy_info)
			proxy_outgoing_ip = self._parse_output_ip(proxy_type)
			proxy_scheme = self._parse_http_type(proxy_type)
			proxy_google_passed = self._parse_google_passed(proxy_line)
			proxy_uri = f"{proxy_scheme}://{proxy_ip}:{proxy_port}/"

			proxy_parsed = ProxyParsed(
				proxy_ip=proxy_ip, proxy_port=proxy_port,
				proxy_scheme=proxy_scheme,
				proxy_level_anonymity=proxy_level_anonymity,
				proxy_country=proxy_country,
				proxy_google_passed=proxy_google_passed,
				proxy_outgoing_ip=proxy_outgoing_ip,
				proxy_uri=proxy_uri)
			return proxy_parsed
		except IndexError as e:
			raise InvalidProxyToParser(e)

	def _parse_anonymity(self, proxy_info):
		if proxy_info.startswith('N'):
			proxy_level_anonymity = 0
		elif proxy_info.startswith('A'):
			proxy_level_anonymity = 1
		elif proxy_info.startswith('H'):
			proxy_level_anonymity = 2
		return proxy_level_anonymity

	def _parse_proxy_type(self, proxy_info):
		try:
			proxy_type = proxy_info[2]
		except IndexError:
			proxy_type = proxy_info[1]
		return proxy_type

	def _parse_google_passed(self, proxy_line):
		if proxy_line.endswith('+'):
			return True
		return False

	def _parse_output_ip(self, proxy_type):
		if proxy_type.endswith('!'):
			return True
		return False

	def _parse_http_type(self, proxy_type):
		if proxy_type.startswith('S'):
			return 'https'
		return 'http'


proxy_api = ProxyListAPI()
proxy_api.initialize()

#print(proxy_api.parse('190.92.9.162:999 HN-N-S -'))
#print(proxy_api.parse('82.114.93.210:8080 AL-N-S! -'))
#print(proxy_api.parse('95.0.90.243:8080 TR-A! + '))
#print(proxy_api.parse('173.46.67.172:58517 US-H -'))

