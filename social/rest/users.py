# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-20010 Universidad Rey Juan Carlos, GSyC/LibreSoft
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
#	 Author : Jose Antonio Santos Cadenas <jcaden __at__ gsyc __dot__ es>
#    Author : Jose Gato Luis <jgato@libresoft.es>


from format.utils import  getResponseFormat, generateResponse
from social.core import api

from social.rest.forms import LoginForm
from utils import error, get_limits, get_num_pages, get_requested_page, generateRESTResponse
from social.privacy2.utils import test_privacy_field_over_nodes
from social.rest.custom_exceptions.rest_interface_exceptions import Bad_Request
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def user_login (request):
	format = getResponseFormat (request)
	if request.method == "POST":
		loginform = LoginForm(request.POST)
		id=loginform.login(request)
		if id:
			data = {'code'		 : '200',
					'id'		   : id,
					'description'  : 'User logged in',}
			return generateResponse(format, data, "ok")
		else:
			return error(format, "User and password do not match") 
	else:
		return error(format, "Need a post petition")

def user_create_or_modify (request, modify=False):
	REGISTER_MANDATORY_FIELDS = []
	REGISTER_OPTIONAL_FIELDS = ["latitude", "longitude", "altitude", "radius", 
								"birthday", "country", "post_code", "first_name", "first_name", "email"]
				
	format = getResponseFormat (request)
	if modify:
		if not request.user.is_authenticated():
			return error(format, "The user is not authenticated")
	if request.method == "POST":
		if ("password" in request.POST) and ("username" in request.POST):
			try:
				passwd=request.POST['password']
				user=request.POST['username']
				p={'username':user,'password':passwd}
  
				for field in REGISTER_MANDATORY_FIELDS:
					print field
					if field in request.POST:
						p[field] = request.POST[field]
					else:
						return error(format ,'Missing parameters')
				
				for field in REGISTER_OPTIONAL_FIELDS:
					if field in request.POST:
						p[field] = request.POST[field]
						
				if ("new_password" in request.POST):  
					p["new_password"]=request.POST["new_password"]

				if modify:
					if user == request.user.username:
						correct, message=api.user.create_or_modify(p, modify=True)
						if correct:
							data = {'code'		 : '200',
									'description'  : 'User modified correctly',}
							return generateResponse(format, data, "ok")
						else:
							return error(format, message)
					else:
						return error(format, "You can not modify your username")
				else:
					correct, message=api.user.create_or_modify(p, modify=False)
					if correct:
						user_id = message
						correct, message = api.node.set_privacy_default(user_id)
						if correct:
							data = {'code'		 : '200',
								'id'		   : user_id,
								'description'  : 'User created correctly',}
							return generateResponse(format, data, "ok")
						else:
							return error(format, message)
					else:
						return error(format, message)
			except ValueError:
				print ValueError
				return error(format ,'Unknown error occurred')			   
		else:
			return error (format, 'Missing parameters')
	else:
		return error (format, 'Need a POST petition')

@csrf_exempt	
def user_set_avatar(request, user=None):
	format = getResponseFormat (request)
	if request.method != "POST":
		return error (format, "Need a POST petition")
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	try:
		photo_id = request.POST["photo_id"]
	except:
		return error(format, "Needs a POST parameter 'photo_id' with the id of the photo")
	correct, message = api.user.set_avatar(request.user.id, photo_id)
	if correct:
		data = {'code'		 : '200',
				'description'  : 'Avatar changed'}
		return generateResponse(format, data, "ok")
	else:
		return error(format, message)
	
@csrf_exempt
def user_set_status(request):
	format = getResponseFormat (request)
	if request.method != "POST":
		return error (format, "Need a POST petition")
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	try:
		status = request.POST["status"]
	except:
		return error(format, "Needs a POST parameter 'status' with the new status")
	correct, message = api.user.set_status(request.user.id, status)
	if correct:
		data = {'code'		 : '200',
				'description'  : 'Status updated'}
		return generateResponse(format, data, "ok")
	else:
		return error(format, message)
	
@csrf_exempt
def user_position (request, user=None):
	format = getResponseFormat (request)
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	if request.method == "POST":
		if user==None:
			u_id=request.user.id
		else:
			u_id=user
		if u_id!=request.user.id:
			return error(format, "You can only modify your position")
		if ("latitude" in request.POST) and ("longitude" in request.POST):
			latitude=request.POST["latitude"]
			longitude=request.POST["longitude"]
			if ("radius" in request.POST):
				radius=request.POST["radius"]
			else:
				radius=None
			if ("altitude" in request.POST):
				altitude=request.POST["altitude"]
			else:
				altitude=None
			if radius != None and altitude != None:
				correct, message = api.node.set_coordinates(u_id, latitude, longitude, altitude=altitude, radius=radius)
			elif radius != None:
				correct, message = api.node.set_coordinates(u_id, latitude, longitude, radius=radius)
			elif altitude != None:
				correct, message = api.node.set_coordinates(u_id, latitude, longitude, altitude=altitude)
			else:
				correct, message = api.node.set_coordinates(u_id, latitude, longitude)
			if correct:
				data = { 'code'		 : '200',
						 'description'  : 'Position updated'}
				return generateResponse(format, data, "ok")
			else:
				return error(format, message)
		else:
			return error (format, 'Missing parameters')
	else:
		return error (format, 'Need a POST petition')

@csrf_exempt
def user_data (request, user):
	format = getResponseFormat (request)
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	p=api.user.get_data(user, request.user)
	if p==None:
		return error (format, 'User doesn\'t exist')
	data = {"code"	: "200",
			"user"	: p,
			"request" : request}
	return generateResponse(format, data, "user/data")

@csrf_exempt
def user_my_data (request):
	format = getResponseFormat (request)
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	return user_data(request, request.user.id)
	
@csrf_exempt	
def user_delete (request):
	format = getResponseFormat (request)
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	if request.method == "POST":
		if ("userid" in request.POST):
			user=request.POST['userid']
			if eval(user) != request.user.id:
				return error(format, "You can only delete your user")
			correct, message=api.user.delete(user)
			if correct:
				data = {'code'		 : '200',
						'description'  : 'User deleted correctly',}
				return generateResponse(format, data, "ok")
			else:
				return error (format, message)			   
		else:
			return error (format, 'Missing parameters')
	else:
		return error (format, 'Need a POST petition')

@csrf_exempt
def user_all(request):
	format = getResponseFormat (request)
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	try:
		users = api.user.get_all(request.user)
	
		return generateRESTResponse(request, users, request.user, str(format))
	
	except Exception, msg:
		return error(format, msg)

@csrf_exempt
def user_friends(request, user=None):
	
	format = getResponseFormat (request)
	
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	
	if user==None:
		user=request.user.id
	
	try:
		users = api.user.get_friends(user, viewer=request.user)
		return generateRESTResponse(request, users, request.user, str(format))
	except Exception, msg:
		return error(format, msg)

@csrf_exempt	
def user_friendship_invitations(request, user=None):
	format = getResponseFormat (request)
	
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	if user==None:
		user=request.user.id
	
	try:
		users = api.user.get_friendship_invitations(user, viewer=request.user)
		return generateRESTResponse(request, users, request.user, str(format))
	except Exception, msg:
		return error(format, msg)

@csrf_exempt
def user_near_friends(request):
	format = getResponseFormat (request)
	
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	
	try:
		radius=request.REQUEST["r"]
	except:
		return error(format, 'Need a (get or post) "r" parameter with the radius')
	
	try:
		users = api.user.get_nearby_friends(request.user.id, radius, request.user)
		return generateRESTResponse(request, users, request.user, str(format))
	except Exception, msg:
		return error(format, msg)

@csrf_exempt
def user_near(request, user=None):
	format = getResponseFormat (request)
	
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	
	try:
		radius=request.REQUEST["r"]
	except:
		return error(format, 'Need a (get or post) "r" parameter with the radius')
	
	if user==None:
		user=request.user.id
		
	try:
		users = api.user.get_nearby_people(user, radius, request.user)
		return generateRESTResponse(request, users, request.user, str(format))
	except Exception, msg:
		return error(format, msg)

@csrf_exempt
def user_photos (request, user=None):
	"""
	@deprecated: this function is deprecated above 1.0 version, search should be done
	using the layer api		
	"""
	format = getResponseFormat (request)
	if not request.user.is_authenticated():
		return error (format, "The user is not authenticated")
	try:
		if user==None:
			user=request.user.id
		f, t, page, elems = get_limits(request)
		photos, n_total_photos = api.photo.get_for_user(user, f, t, request.user)
		
		total_pages = get_num_pages(n_total_photos, elems)
		
		data = {"code"   : "200", 
				"page"   : page,
				"elems"   : len(photos),
				"total_pages" : total_pages,
				"results" : photos }				
		
		return generateResponse(format, data, "node/list")
	except:
		return error(format, 'Some errors occurred')	
	
@csrf_exempt
def user_sounds (request, user=None):
	"""
	@deprecated: this function is deprecated above 1.0 version, search should be done
	using the layer api		
	"""
	format = getResponseFormat (request)
	if not request.user.is_authenticated():
		return error (format, "The user is not authenticated")
	try:
		if user==None:
			user=request.user.id
		f, t, page, elems = get_limits(request)
		sounds, n_total_sounds = api.sound.get_for_user(user, f, t, request.user)
		
		total_pages = get_num_pages(n_total_sounds, elems)
		
		data = {"code"   : "200", 
				"page"   : page,
				"elems"   : len(sounds),
				"total_pages" : total_pages,
				"results" : sounds }				
		
		return generateResponse(format, data, "node/list")
	except:
		return error(format, 'Some errors occurred')

@csrf_exempt
def user_notes (request, user=None):
	"""
	@deprecated: this function is deprecated above 1.0 version, search should be done
	using the layer api		
	"""
	format = getResponseFormat (request)
	if not request.user.is_authenticated():
		return error (format, "The user is not authenticated")
	try:
		if user==None:
			user=request.user.id
		f, t, page, elems = get_limits(request)
		notes, n_total_notes = api.note.get_for_user(user, f, t, request.user)
		
		total_pages = get_num_pages(n_total_notes, elems)
		
		data = {"code"   : "200", 
				"page"   : page,
				"elems"   : len(notes),
				"total_pages" : total_pages,
				"results" : notes }				
		
		return generateResponse(format, data, "node/list")
	except:
		return error(format, 'Some errors occurred')

@csrf_exempt
def user_relation (request):
	format = getResponseFormat (request)
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	if request.method=='POST':
		if ("userid1" in request.POST) and ("userid2" in request.POST):
			user1=request.POST['userid1']
			user2=request.POST['userid2']
			correct, message=api.user.create_friendship(user1, user2)
			if correct:
				data = {'code'		 : '200',
					   'description'   : 'Relation created correctly',}
				return generateResponse(format, data, "ok")
			else:
				return error (format, message)
		else:
			return error (format, 'Missing parameters')
	else:
		return error (format, 'Need a POST petition')

@csrf_exempt
def user_relation_delete (request):
	format = getResponseFormat (request)
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	if request.method=='POST':
		if ("userid1" in request.POST) and ("userid2" in request.POST):
			user1=request.POST['userid1']
			user2=request.POST['userid2']
			correct, message=api.user.delete_friendship(user1, user2)
			if correct:
				data = {'code'		: '200',
					   'description'  : 'Relation deleted correctly',}
				return generateResponse(format, data, "ok")
			else:
				return error (format,  message)
		else:
			return error (format, 'Missing parameters')
	else:
		return error (format, 'Need a POST petition')
	
@csrf_exempt
def user_groups (request):
	format = getResponseFormat (request)
	if not request.user.is_authenticated():
		return error(format, "The user is not authenticated")
	try:
		groups=api.group.get_for_user(request.user)
		data = {'code'	  : '200',
				'groups'   : groups}
		return generateResponse(format, data, "group/list")
	except:
		return error(format, 'Some errors occurred')

