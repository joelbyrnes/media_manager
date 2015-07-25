import transmissionrpc
import os
import sys
import datetime
import csv

complete_dir = '/home/joel/mac-mini.joel/Media Downloads/completed'
out_dir = '/home/joel/mac-mini.joel/Media Downloads/out_tv'

def find_first_rar(files):
	def subfilter(fs):
		for f in fs:
			print "(found rar-like file %s)" % f
			if ".subpack." in f.lower():
				print "(looks like subpack, ignoring)"
			else:
				return f

	rars = filter(lambda f: f.lower().endswith(".rar"), files)
	rar = subfilter(rars)
	if rar:
		return rar

	r00s = filter(lambda f: f.lower().endswith(".r00"), files)
	r00 = subfilter(r00s)
	if r00:
		return r00

	return None

def walk_path(path, function):
	if not os.path.exists(path): raise Exception("path does not exist: " + path)
	# if not os.path.isdir(path): return False

	for root, subdirs, files in os.walk(path):
		yield function(files)

def dir_has_rars(path):
	if not os.path.exists(path): raise Exception("path does not exist: " + path)
	if not os.path.isdir(path): return False

	for root, subdirs, files in os.walk(path):
		if find_first_rar(files) != None:
			return True
	return False

def move(names, cwd, out_dir):
	for f in names:
		print "moving %s to %s/%s" % (f, out_dir, f)
		os.rename("%s/%s" % (cwd, f), "%s/%s" % (out_dir, f))

def main(complete_dir, out_dir, actually_move):

	tc = transmissionrpc.Client('mac-mini.local', port=9091)
	torrents = tc.get_torrents()

	tdict = {t.name: t for t in torrents}

	on_disk = [x for x in os.listdir(complete_dir) if not x.startswith(".")]

	print "%d paths to check" % len(on_disk)
	print "%d torrents" % len(torrents)
	print ''

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
	print ''

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
	if to_move:
		if actually_move:
			move([c['name'] for c in to_move], complete_dir, out_dir)
			print ''
		else:
			print "not actually moving files as flag not set"
	else:
		print 'nothing to move'


def find_rars(files):
	for f in files:
		if f.lower().endswith(".rar") or f.lower().endswith(".r00"):
			print "(found rar-like file %s)" % f
			if ".subpack." in f.lower():
				print "(looks like subpack, ignoring)"
			else:
				yield f


# figure out if we need to extract and do it
def extract(complete_dir, folder):

	path = complete_dir + "/" + folder
	print path
	# print dir_has_rars(path)
	# for x in walk_path(path, find_rars):
	# 	for y in x:
	# 		print y

	os.chdir(complete_dir)

	for root, subdirs, files in os.walk(folder):
		print "-- " + root
		rar = find_first_rar(files)
		if rar:
			print "extract " + root + "/" + rar + " to (dest folder)/" + root
		else:
			if subdirs:
				print "dir has subdirs but no rars: mkdir"
			if not subdirs:
				print "dir has no subdirs: copy"

	print "done; delete " + folder

if __name__ == "__main__":
	# extract(complete_dir, "The.Walking.Dead.S05E09.720p.HDTV.x264-KILLERS")
	# extract(complete_dir, "Parks.and.Recreation.S03.DVDRip.XviD-REWARD")

	main(complete_dir, out_dir, False)
