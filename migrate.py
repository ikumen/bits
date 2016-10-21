import os
import sys
import argparse
import re
import yaml
import requests
import json
import datetime

def migrate(path, token):
	headers = {'Authorization': 'token ' + token}
	for file in os.listdir(path):
		if not file.startswith('_'):
			with open(os.path.join(path, file)) as input:
				post = _parse(input.read())
				requests.post('https://api.github.com/gists', headers=headers,
					data=json.dumps({
							'description': post['fmatter']['title'],
							'public': False,
							'files': {
									file: {
										'content': ''.join(['---\n', yaml.dump(post['fmatter']), '---\n\n', post['content']])
									}
								}
						}))


def _parse(s):
	matches = re.search(r'^---(.*?)---\s*(.*)', s, re.DOTALL)
	if matches:
		fmatter = _parse_frontmatter(matches.groups()[0])
		if not fmatter:
			return None
	return {'fmatter': fmatter, 'content': matches.groups()[1]}


def _parse_frontmatter(s):
	# remove double quotes
	s = s.replace('"', '')
	fmatter = {}
	pairs = re.findall(r'(tags|date|title|layout|category):(.*)', s)
	for pair in pairs:
		key = pair[0]
		value = pair[1].strip()
		if key == 'tags':
			value = value.split(' ')
		elif key == 'date':
			key = 'created_at'
			value = datetime.datetime.strptime(value, '%Y-%m-%d')
		fmatter[key] = value
	return fmatter

def main():
	parser = argparse.ArgumentParser(description="""
		Script for migratin Jekyll pages to GitHub Gist for bits 
		project (https://github.com/ikumen/bits)
		""")
	
	parser.add_argument('--token', required=True, 
		help='GitHub personal or OAuth access token (not password)')
	parser.add_argument('--path', required=True, 
		help='Directory containing Jekyll posts to migrate')

	args = parser.parse_args()

	if not os.path.isdir(args.path):
		print('"{}" is not a valid directory.'.format(args.path))
		sys.exit(2)

	migrate(args.path, args.token)

if __name__ == '__main__':
	main()