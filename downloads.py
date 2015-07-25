import transmissionrpc
import os
import sys
import datetime
import csv

complete_dir = '/home/joel/mac-mini.joel/Media Downloads/completed'
out_dir = '/home/joel/mac-mini.joel/Media Downloads/out_tv'

def list_has_rars(files):
	for f in files:
		if f.lower().endswith(".rar") or f.lower().endswith(".r00"):
			print "(found rar-like file %s)" % f
			return True
	return False

def dir_has_rars(path):
	if not os.path.exists(path): raise Exception("path does not exist: " + path)
	if not os.path.isdir(path): return False

	for root, subdirs, files in os.walk(path):
		if list_has_rars(files):
			return True
	return False

def move(names, cwd, out_dir):
	for f in names:
		print "moving %s to %s/%s" % (f, out_dir, f)
		os.rename("%s/%s" % (cwd, f), "%s/%s" % (out_dir, f))

def main(complete_dir, out_dir):

	tc = transmissionrpc.Client('mac-mini.local', port=9091)
	torrents = tc.get_torrents()

	tdict = {t.name: t for t in torrents}

	on_disk = [x for x in os.listdir(complete_dir) if not x.startswith(".")]

	def create_data(p):
		torrent = tdict[p] if p in tdict else None
		path = complete_dir + "/" + p
		data = {'name': p, 'path': path, 'torrent': torrent, 'is_dir': os.path.isdir(path)}
		# print data
		return data

	possibles = map(create_data, on_disk)

	print "single files: "
	for x in [c for c in possibles if not c['is_dir']]:
		print x

	no_torrent = [c for c in possibles if not c['torrent']]
	print "no torrent:"
	for c in no_torrent:
		c['has_rars'] = dir_has_rars(c['path'])
		print "** NOT in Tx: " + c['name']

	to_extract = [c for c in possibles if not c['torrent'] and c['has_rars']]

	print ''
	print "no torrent but has rars, to extract and/or delete:"
	for c in to_extract:
		print c['name']

	to_move = [c for c in possibles if not c['torrent'] and not c['has_rars']]

	print ''
	print "no torrent and has no rars:"
	for c in to_move:
		print c['name']

	print ''

	move([c['name'] for c in to_move], complete_dir, out_dir)
	print ''

if __name__ == "__main__":

	# path = complete_dir + "/The.Walking.Dead.S05E09.720p.HDTV.x264-KILLERS"
	# print path
	# print dir_has_rars(path)

	main(complete_dir, out_dir)
