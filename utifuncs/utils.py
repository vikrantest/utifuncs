import json
import re
import random
import string
from pygeocoder import Geocoder
from math import *
from django.http import HttpResponse
import urllib2
import urllib
import json
import datetime
import calendar
import locale
import dateutil.parser
import time
import pytz
import boto
from boto.s3.key import Key
import uuid
import os
import requests
import itertools
import six
from math import radians, cos, sin, asin, sqrt
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.conf import settings as my_settings
from django.template import loader, Context
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from common.constants import *
from email.MIMEImage import MIMEImage
#from urlparse import urlparse

import logging
logger = logging.getLogger(__name__)

START_YEAR = 1990
END_YEAR = 2050
UNIT = 'kms'
#UNIT = 'miles'
radian = 3600000.00
TIME_ZONE = pytz.timezone("Asia/Kolkata")


def get_speed(speed):
	try:
		speed  = 0.036*speed
		if speed < 2.00:speed = 0
		return speed
	except:
		return 0


class GoogleApiServices():
	"""
	integrating various google APIs
	"""
	def __init__(GOOGLE_API_KEY):
		self.API_KEY = GOOGLE_API_KEY




	def get_trip_path_distance(self,start_loc_lat,start_loc_lon,end_loc_lat,end_loc_lon,start_time=None):
		current_time = local_unixtime()
		url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins='+str(start_loc_lat)+','+str(start_loc_lon)+'&destinations='+str(end_loc_lat)+','+str(end_loc_lon)+'&mode=car&language=en-US&departure_time='+str(current_time)+'&key='+self.API_KEY
		print url
		response = urllib2.urlopen(url)
		data = json.load(response)
		vals = 0
		try:
			dist = data['rows'][0]['elements'][0]['distance']['text']#### to-do USE VALUE INSTEAD OF TEST
			dist = dist.replace('km','').strip()
			dist = dist.replace('m','').strip()
			dist = float(dist.replace(',',''))
			vals = data['rows'][0]['elements'][0]['distance']['value']

		except:
			try:
				dist = data['rows'][0]['elements'][0]['distance']['text']
				import sys
				print sys.exc_info()
				dist = dist.replace('m','').strip()
				dist = float(dist.replace(',',''))
			except:dist = 0.00
		print vals
		distance = float(vals)/1000
		print distance
		try:
			time = data['rows'][0]['elements'][0]['duration']['text']
			seconds_time = data['rows'][0]['elements'][0]['duration']['value']
		except:seconds_time , time= 0,None
		return  distance , time , seconds_time

	def calculate_distance_point_sets(lat_lon_list):
		try:
			distance = 0
			elem_1 = lat_lon_list
			for points in lat_lon_list:
				#if elem_1:
				p_distance = distance_between_points(points[0],points[1],elem_1[0],elem_1[1])
				p_distance
				distance +=p_distance
				elem_1 = points
			return distance
		except:
			return 0.00


	def __decode_line(encoded):
		encoded_len = len(encoded)
		index = 0
		array = []
		lat = 0
		lng = 0
		while index < encoded_len:
			b = 0
			shift = 0
			result = 0
			while True:
				b = ord(encoded[index]) - 63
				index = index + 1
				result |= (b & 0x1f) << shift
				shift += 5
				if b < 0x20:
					break
			dab = ~(result >> 1) if result & 1 else result >> 1
			lat += dab
			shift = 0
			result = 0
			while True:
				b = ord(encoded[index]) - 63
				index = index + 1
				result |= (b & 0x1f) << shift
				shift += 5
				if b < 0x20:
					break
			dlng = ~(result >> 1) if result & 1 else result >> 1
			lng += dlng
			array.append((lat * 1e-5, lng * 1e-5))
		return array


	def distance_between_points(lat1, lon1, lat2, lon2):
		try:
			if UNIT == 'miles':radius = 3959
			else:radius = 6371
			distance = radius * acos( cos( radians(lat1) ) * cos( radians( lat2 ) ) * cos( radians( lon2) - radians(lon1) ) + sin( radians(lat1) ) * sin( radians( lat2 ) ) )
			return distance
		except:
			import sys
			print sys.exc_info()
			return 0.00


	def get_lat_lon(self,address):
		try:
			try:result = Geocoder(self.API_KEY).geocode(str(address))
			except:
				try:result = Geocoder.geocode(str(address))
				except:result=None

			return result
		except:return None

	def get_breadcrum(st_lat,st_lon,end_lat,end_lon):
		final_result=[]
		url = 'https://maps.googleapis.com/maps/api/directions/json?origin='+str(st_lat)+','+str(st_lon)+'&destination='+str(end_lat)+','+str(end_lon)+'&sensor=false&key='+self.API
		response = urllib2.urlopen(url)
		data = json.load(response)
		for step in data["routes"][0]["legs"][0]["steps"]:
			latlngs = __decode_line(step["polyline"]["points"])
			for latlng in latlngs:
				final_result.append([latlng[0],latlng[1]])
		return final_result

	def get_tiny_url(main_url):
		service_url = "https://www.googleapis.com/urlshortener/v1/url?key="+self.API_KEY
		data=str({'longUrl':str(main_url)})
		response = requests.post(service_url,data=data,headers={"Content-Type":"application/json"})
		if response.status_code == 200:
			f_response = response.json()
			tiny_url = f_response['id']
		else:
			tiny_url = main_url
		return tiny_url


	def get_address(self,lat, lon):
		try:
			# quadrim key: AIzaSyCsNm4ev8ZEEhiWhfF-NxZHeGXI_dhQ1Zk
			# Productiom : AIzaSyDGqPBq3MAGBgx4raPK3n55VkMfSf1BIYI
			location = Geocoder(self.API_KEY).reverse_geocode(lat, lon)
			try:
				short_address = str(location[0].route)
			except:
				short_address = None
			try:
				long_address = str(location[0])
			except:
				long_address = None
			address = (short_address,long_address)
		except:
			address = (None,None)
		return address







class RequestValidationsAndValidation():


	def __init__(self):
		self.fields = data_fields
		self.validate_fields = fields



	def mandatory_validation(self):
		"""Fuction to check for mandatory fields"""
		for key in self.fields:
			if not self.validate_fields.get(key):
				return key
		return True


	def validate_number_fields(self, data_fields, negative_allowed=False):
		for field in self.validate_fields:
			value = self.validate_fields.get(field,None)
			if value:
				try:
					f = float(value)
				except ValueError:
					return field
				if not negative_allowed and f < 0:
					return field
		return None

	def get_format_req(self,query_dict):
		query_dict = self.request_dict
		query_dict = dict(query_dict)
		for k,v in query_dict.items():
			if isinstance(v,list) and len(v) == 1:
				if isinstance(v[0],str) or isinstance(v[0],unicode):
					query_dict[k]=v[0]
			else:
				pass
		return query_dict


	def convert_query_dict_to_dict(self,query_dict):
		query_dict = self.request_dict
		query_dict = dict(query_dict)
		data_dict = {}
		for key, value in query_dict.items():
			if isinstance(value,list) and len(value) == 1:
				if isinstance(value[0],str) or isinstance(value[0],unicode):
					data_dict[key]=value[0]
				else:
					pass
		return data_dict


def get_unix_date_diff(start,end):
	try:return int(start.strftime('%s')),int(end.strftime('%s'))
	except:return  None

def get_unix_dateime_range(hours,days):
	if days == 0:days = 1
	return int(60*60*hours*days)


def sec_to_time(sec):
	days = sec / 86400
	sec -= 86400*days
	hrs = sec / 3600
	sec -= 3600*hrs
	mins = sec / 60
	sec -= 60*mins
	duration = ''
	if days > 0:
		duration += '%s days '% days
	if hrs > 0:
		duration += '%s hrs '% hrs
	if mins > 0:
		duration += '%s mins'% mins
	return duration









def local_unixtime(seconds=None):
	#if seconds:return seconds+19800
	#else:
	return int(time.time())

def get_midnight_time(seconds=None):
	if not seconds:
		time_now = datetime.datetime.now()
	else:
		time_now = get_local_time(seconds)
	time_at_start_of_today = datetime.datetime(time_now.year, time_now.month, time_now.day)
	return int(time.mktime(time_at_start_of_today.timetuple()))

def local_to_utc(time_obj,type=""):
	if 'utc' in type:return time_obj
	else:return time_obj-19800


def get_lat_lon_cor(val,type=None):
	val = float(val)/radian
	return val





class PolylineCodec(object):
	def _pcitr(self, iterable):
		return six.moves.zip(iterable, itertools.islice(iterable, 1, None))

	def _write(self, output, value):
		coord = int(round(value * 1e5, 0))
		coord <<= 1
		coord = coord if coord >= 0 else ~coord

		while coord >= 0x20:
			output.write(six.unichr((0x20 | (coord & 0x1f)) + 63))
			coord >>= 5

		output.write(six.unichr(coord + 63))

	def _trans(self, value, index):
		byte, result, shift = None, 0, 0

		while (byte is None or byte >= 0x20):
			byte = ord(value[index]) - 63
			index += 1
			result |= (byte & 0x1f) << shift
			shift += 5
			comp = result & 1

		return ~(result >> 1) if comp else (result >> 1), index

	def decode(self, expression):
		coordinates, index, lat, lng, length = [], 0, 0, 0, len(expression)

		while (index < length):
			lat_change, index = self._trans(expression, index)
			lng_change, index = self._trans(expression, index)
			lat += lat_change
			lng += lng_change
			coordinates.append((lat / 1e5, lng / 1e5))

		return coordinates

	def encode(self, coordinates):
		output = six.StringIO()
		self._write(output, coordinates[0][0])
		self._write(output, coordinates[0][1])

		for prev, curr in self._pcitr(coordinates):
			self._write(output, curr[0] - prev[0])
			self._write(output, curr[1] - prev[1])

		return output.getvalue()












def get_time_filter_from_list(data,start,end):
	rows=[]
	for dat in data:
		if dat[4]>start:
			rows.append(dat)
		else:pass
	data_len = len(rows)
	tem_dict={}
	for indx,dat in enumerate(data):
		tem_dict[dat[4]] = str(indx)
	vals =  tem_dict.keys()
	if vals:
		end_value = min(vals, key=lambda x:abs(x-end))
		rows.append(data[int(tem_dict[end_value])])
		data_len = len(rows)
		del vals
		del tem_dict
		del data
		distance_travelled=fuel_consumed=0
		try:
			for ind,row in enumerate(rows):
				if row[2] == 0 and ind-1>0:
					# print cur_dist,row , rows[cur_dist-1][2]
					# print rows[cur_dist-1],cur_dist-1,row,cur_dist
					distance_travelled += rows[ind-1][2]
				if row[3] == 0 and ind-1>0:
					fuel_consumed += rows[ind-1][3]
			distance_travelled = (float(distance_travelled + int(rows[data_len-1][2])) - float(rows[0][2]))/1000
			print distance_travelled
			fuel_consumed = (float(fuel_consumed + int(rows[data_len-1][3])) - float(rows[0][3]))/10000
		except:
			from common.utils import send_mail
			import sys
			print sys.exc_info()
			distance_travelled=fuel_consumed=0
		return distance_travelled,fuel_consumed
	else:return 0,0





def get_id_from_num(id, precision=2):
	"""
	convert number to string with min length equal to precision'
	"""
	base = 26
	alpha_num_dict = get_alpha_num_dict()
	def convert_num_to_alpha_string(num):
		"""Recursive function to convert num to alphabetic string"""
		div = num/base
		if num == 0:
			return ''
		else:
			return convert_num_to_alpha_string(div) + alpha_num_dict[num % base + 1]

	for i in range(1, precision-1):
		base *= base
	id += base
	alpha_id = convert_num_to_alpha_string(id)
	return alpha_id



def get_local_time(unix=None):
	if not unix:
		unix = local_unixtime()
	dates = datetime.datetime.utcfromtimestamp(int(unix))
	dates = dates.replace(tzinfo=pytz.utc)
	dates = dates.astimezone(TIME_ZONE)
	return dates


def get_current_month_year(start_time):
	dt = datetime.datetime.utcfromtimestamp(start_time)
	dt = dt.replace(tzinfo=pytz.utc)
	dt = dt.astimezone(TIME_ZONE)
	month = dt.strftime('%B').lower()
	year = dt.strftime('%y')
	current_time = local_unixtime()
	dat = datetime.datetime.utcfromtimestamp(current_time)
	dat = dat.replace(tzinfo=pytz.utc)
	dat = dat.astimezone(TIME_ZONE)
	current_month = dat.strftime('%B').lower()
	current_year = dat.strftime('%y')
	current = True if current_month == month else False
	return current , month , year


def move_file_cloud_storage(file=None, file_content=None, file_name=None, folder='reports', delete_server_file=True):
	if not file and not file_content:
		raise Exception('Missing mandatory field: file/file_content')
	folder = my_settings.MEDIA_ROOT + folder
	if file:
		ext = os.path.splitext(file)[1]
	elif file_name:
		ext = os.path.splitext(file_name)[1]
	else:
		ext = '.txt'
	if not file_name:
		file_name = uuid.uuid4()
	conn = boto.connect_gs(my_settings.GS_ACCESS_KEY_ID, my_settings.GS_SECRET_ACCESS_KEY)
	bucket = conn.get_bucket(my_settings.GS_BUCKET_NAME)
	k = Key(bucket)
	k.key = '{}/{}{}'.format(folder, file_name, ext)
	if file:
		k.set_contents_from_filename(file)
		if delete_server_file:
			os.remove(file)
	else:
		k.set_contents_from_string(file_content)
	k.set_acl('public-read')
	return k.generate_url(0, query_auth=False, force_http=True)


def save_image_from_url(url, destination_path, file_name):
	image_file = os.path.join(destination_path, file_name)
	try:
		if not os.path.exists(destination_path):
			os.makedirs(destination_path)
			os.chmod(destination_path, 1777)
		with open(image_file, 'wb') as f:
			os.chmod(image_file, 0o777)
			res = requests.get(url)
			if res.status_code == 200:
				f.write(res.content)
			else:
				image_file = None
	except:
		image_file = None
	return image_file



def generate_token():
	log = str(datetime.datetime.now().strftime('%Y-%m-%d'))
	logs = hashlib.sha256(log)
	token = str(logs.hexdigest())
	return token

def validate_token(token):
	log = str(datetime.datetime.now().strftime('%Y-%m-%d'))
	logs = hashlib.sha256(log)
	out = str(logs.hexdigest())
	if token == out:
		return True
	else:
		return False




class RequestHandler(object):
	def __init__(self,query_dict):

		self.request_dict = query_dict



	def get_format_req(query_dict):
		query_dict = self.request_dict
		query_dict = dict(query_dict)
		for k,v in query_dict.items():
			if isinstance(v,list) and len(v) == 1:
				if isinstance(v[0],str) or isinstance(v[0],unicode):
					query_dict[k]=v[0]
			else:
				pass
		return query_dict


	def convert_query_dict_to_dict(query_dict):
		query_dict = self.request_dict
		query_dict = dict(query_dict)
		data_dict = {}
		for key, value in query_dict.items():
			if isinstance(value,list) and len(value) == 1:
				if isinstance(value[0],str) or isinstance(value[0],unicode):
					data_dict[key]=value[0]
				else:
					pass
		return data_dict


