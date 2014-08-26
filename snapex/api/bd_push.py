import hashlib
import time
import requests
import urllib

APIKEY = '4vvtke0DV3yR9bIYcGyDvKBC'
SECRETKEY = '1B65i354OUTyyyVxMhI9IlgBxFztCp84'
method = 'POST'
PUSH_TYPE = 1

def push_msg(user_id, channel_id, msg):
	'''
		user_id: string
		channel_id: uint
		msg: {
			'title': 'the msg title',
			'description': 'the msg details'
		}
	'''
	try:
		url = 'http://channel.api.duapp.com/rest/2.0/channel/channel'
		args = dict()
		args['method'] = 'push_msg'
		args['apikey'] = APIKEY
		args['user_id'] = user_id
		args['push_type'] = PUSH_TYPE
		args['channel_id'] = channel_id
		args['messages'] = str(msg)
		args['msg_keys'] = 'new_plan'
		args['timestamp'] = int(time.time())
		
		# generate sign
		gather = method + url
		keys = args.keys()
		keys.sort()
		for key in keys:
			gather += key + '=' + str(args[key])
		gather += SECRETKEY
		sign = hashlib.md5(urllib.quote_plus(gather))
		args['sign'] = sign.hexdigest()

		response = requests.post(url, data=args, timeout=5)
		data = response.content
		import simplejson
		amount = simplejson.loads(data)['response_params']['success_amount']
		if amount>0:
			return 0, 'ok'
		else:
			return 1, '0 msg pushed!'
	except Exception as e:
		return 1, str(e)

if __name__ == '__main__':
	channel_id = 4080370122348418907
	user_id = "878635970825842092"
	msg = {'title':'baidu push', 'description': 'the msg details'}
	push_msg(user_id, channel_id, msg)