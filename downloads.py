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

def print_possibles(possibles, tnames):
	for p in possibles:
		if p in tnames:
			print "Tx: " + p
			pass
		else:
			print "** NOT in Tx: " + p

			if dir_has_rars(complete_dir + "/" + p):
				print "  ** HAS RARS"


def main(complete_dir, out_dir):

	tc = transmissionrpc.Client('mac-mini.local', port=9091)
	torrents = tc.get_torrents()

	tnames = [t.name for t in tc.get_torrents()]

	possibles = [x for x in os.listdir(complete_dir) if not x.startswith(".")]

	print_possibles(possibles, tnames)

	print ""
	print "mkvs:"
	mkvs = filter(lambda p: p.lower().endswith(".mkv"), possibles)

	print_possibles(mkvs, tnames)

	print ''
	print 'to move  if not f in tnames and not dir_has_rars(f)   :'

	to_move = [f for f in possibles if not f in tnames and not dir_has_rars(complete_dir + "/" + f)]

	for f in to_move:
		print f

	print ''
	print 'to move  if not f in tnames and dir_has_rars(f):'

	not_to_move = [f for f in possibles if not f in tnames and dir_has_rars(complete_dir + "/" + f)]

	# for f in not_to_move:
	# 	print f + "  ** HAS RARS"

	print ''

	#move(to_move, complete_dir, out_dir)
	#print ''

if __name__ == "__main__":

	# path = complete_dir + "/The.Walking.Dead.S05E09.720p.HDTV.x264-KILLERS"
	# print path
	# print dir_has_rars(path)

	main(complete_dir, out_dir)
