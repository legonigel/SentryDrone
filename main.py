import lib.libardrone
import boto3
import boto
from boto.s3.key import Key

def searchTarget(drone):
	c = boto.connect_s3()
	b = c.get_bucket('targetxandydata')
	k = Key(b)
	k.key = 'x'
	x = k.get_contents_as_string()
	k.key = 'xMax'
	xMax = k.get_contents_as_string()
	
	error = 40
	
	if x < xMax/2 - error:
		# need to turn right
		print "1"
	elif x > xMax/2 + error:
		# need to turn left
		print "2"
	
	if(x )

def main():
	sqs = boto3.resource('sqs', region_name="us-east-1")
	q = sqs.get_queue_by_name(QueueName="DroneQueue")
	q.purge()
		

	drone = lib.libardrone.ARDrone(True)
	print "Connected to Drone"
	done = False
	try:
		while not done:
			rs = q.receive_messages()
			for m in rs:
				body = m.body
				if body == "reset":
					body = "emergency"
				if body == "search":
					searchTarget(drone)
				drone.apply_command(body)
				m.delete()
	except (KeyboardInterrupt, SystemExit):
		drone.halt()

if __name__ == '__main__':
	main()
