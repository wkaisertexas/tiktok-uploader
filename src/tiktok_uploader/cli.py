"""
CLI is a controller for the command line use of this library
"""

from argparse import ArgumentParser
from tiktok_uploader.upload import upload_video

from os.path import exists

def cli():
	"""
	Passes arguments into the program
	"""
	args = get_args()
	
	args = validate_args(args=args)
	
	# runs the program using the arguments provided
	upload_video(**args) # TODO: check if unpacking arguemnts in this way works	

def get_args():
	"""
	Generates a parser which is used to get all of the video's information
	"""
	parser = ArgumentParser(
		description='TikTok uploader is a video uploader which can upload a video from your computer to the TikTok using selenium automation'
	)
	
	# primary arguments		
	parser.add_argument('-v', '--video', 'Video file')
	parser.add_argument('-d', '--description', 'Description')
	
	# authentication arguments
	parser.add_argument('-c', '--cookies', help='The cookies you want to use')
	parser.add_argument('-u', '--username', help='Your TikTok email / username')
	parser.add_argument('-p', '--password', help='Your TikTok password')
		
	# selenium arguments
	parser.add_argument('-h', '--headless', default=False, action='store_true', help='Whether or not the browser should be run in headless mode')
	return parser.parse_args()


def validate_args(args: dict):
	"""
	Preforms validation on each input given
	"""

	# Makes sure the video file exists
	if not exists(args['video']):
		raise FileNotFoundError(f'Could not find the video file at {args["video"]}')

	# User can not pass in both cookies and username / password
	if args['cookies'] and (args['username'] or args['password']):
		raise ValueError('You can not pass in both cookies and username / password')
	
	return args
