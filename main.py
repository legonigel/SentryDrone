import lib.libardrone
import boto3
import boto
from boto.s3.key import Key
from time import sleep

def searchTarget(drone):
	c = boto.connect_s3()
	b = c.get_bucket('targetxandydata')
	k = Key(b)
	k.key = 'x'
	x = k.get_contents_as_string()
	k.key = 'xMax'
	xMax = k.get_contents_as_string()
	
	error = 40
	
	if x < (xMax/2 - error):
		# need to turn right
		drone.turn_left(0.1)
		return False
	elif x > (xMax/2 + error):
		# need to turn left
		drone.turn_left(0.1)
		return False
	else:
		drone.hover()
		return True
	
def main():
	print "Connecting to AWS"
	sqs = boto3.resource('sqs', region_name="us-east-1")
	q = sqs.get_queue_by_name(QueueName="DroneQueue")
	try:
		q.purge()
	except:
		pass
	print "Finished with AWS"

	drone = lib.libardrone.ARDrone(True)
	print "Connected to Drone"
	drone.reset()
	done = False
	has_target = True
	try:
		while not done:
			print ".",
			rs = q.receive_messages()
			if not rs:
				continue
			for m in rs:
				body = m.body
				if body == "reset":
					body = "emergency"
				print "Got command", body
				if body == "search" or not has_target:
					has_target = searchTarget(drone)
				elif body == "spin":
					drone.event_turnarround()
				elif body == "flip":
					drone.event_flip()
				elif body == "turn_left":
					drone.turn_left(0.1)
				elif body == "turn_right":
					drone.turn_right(0.1)
				else:
					drone.apply_command(body)
				m.delete()
			sleep(0.5)
	except (KeyboardInterrupt, SystemExit):
		drone.halt()

if __name__ == '__main__':
	main()
