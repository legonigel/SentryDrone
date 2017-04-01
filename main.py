import lib.libardrone
import boto3

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
				drone.apply_command(body)
				m.delete()
	except (KeyboardInterrupt, SystemExit):
		drone.halt()

if __name__ == '__main__':
	main()
