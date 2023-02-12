"""
CLI is a controller for the command line use of this library
"""

from argparse import ArgumentParser
from .upload import upload_video

def cli():
	"""
	Passes arguments into the program
	"""
	args = get_args()
	
	args = validate_args()
	
	# runs the program using the arguments provided
	upload_video(*args) # TODO: check if unpacking arguemnts in this way works
	

def get_parser():
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
	parser.add_argument('-c', '--cookies', 'The cookies you want to use')
	parser.add_argument('-u', '--username', 'Your TikTok email / username')
	parser.add_argument('-p', '--password', 'Your TikTok password')
		
	# selenium arguments
	parser.add_argument('-h', '--headless', 'Whether or not the browser should be run in headless mode')

	return parser.parse_args()


def validate_args(args: dict):
	"""
	Preforms validation on each input given
	"""
	return args
