import transmissionrpc
import os
import sys
import datetime
import csv
import re

complete_dir = '/home/joel/mac-mini.joel/Media Downloads/completed'
out_dir = '/home/joel/mac-mini.joel/Media Downloads/out_tv'

def find_first_rar(files):
	def subfilter(fs):
		for f in fs:
			if ".subpack." in f.lower() or "/subs/" in f.lower() or "subs" in f.lower():
				# print "(found rar-like file %s that looks like subpack, ignoring)"
				pass
			else:
				# print "(found rar-like file %s)" % f
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

def printall(candidates, title):
	print title
	print len(candidates)
	for c in candidates:
		print c['name']
	print ''

def write_report(filename, candidates):
	with open(filename, 'wb') as f:
		output_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
		output_writer.writerow([
			'name',
			'has_torrent',
			'date_added',
			'status',
			'error',
			'errorString',
			'isFinished',
			'is_dir',
			'has_rars',
			'action',
			])
		for c in candidates:
			t = c['torrent']

			row = [
				c['name'],
				t is not None,
				t.date_added if t else None,
				t.status if t else None,
				t.error if t else None,
				t.errorString if t else None,
				t.isFinished if t else None,
				c['is_dir'],
				c['has_rars'],
				]

			if t and t.error != 0:
				print t, t.error, t.errorString

			if not t and not c['has_rars']:
				row.append('move')
			elif not t and c['has_rars']:
				row.append('extract and delete files')
			elif (t and t.isFinished) and not c['has_rars']:
				row.append('move and remove torrent')
			elif (t and t.status == "stopped" and t.error == 0) and not c['has_rars']:
				row.append('move and remove torrent')
			elif (t and t.status == "stopped" and t.error == 0) and c['has_rars']:
				row.append('extract files and remove torrent and data')

			elif t and t.status == "seeding" or t.status == "downloading" or t.status == "download pending":
				row.append('-')
			else:
				row.append('???')
			output_writer.writerow(row)

def main(complete_dir, out_dir, take_action):

	tc = transmissionrpc.Client('mac-mini.local', port=9091)
	torrents = tc.get_torrents()

	tdict = {t.name: t for t in torrents}

	on_disk = [x for x in os.listdir(complete_dir) if not x.startswith(".")]

	print "%d paths to check" % len(on_disk)
	print "%d torrents" % len(torrents)

	def create_data(p):
		torrent = tdict[p] if p in tdict else None
		path = complete_dir + "/" + p
		data = {'name': p, 'path': path, 'torrent': torrent, 'is_dir': os.path.isdir(path),
				'has_rars': dir_has_rars(path)}
		# print data
		return data

	possibles = map(create_data, on_disk)

	write_report("report.csv", possibles)
	print "wrote report to report.csv"

	print ''

	# printall([c for c in possibles if not c['is_dir']], "single files:")

	to_move = [c for c in possibles if not c['torrent'] and not c['has_rars']]

	to_remove = [c for c in possibles if (c['torrent'] and c['torrent'].isFinished) and not c['has_rars']]
	to_remove.extend([c for c in possibles if (c['torrent'] and c['torrent'].status == "stopped" and c['torrent'].error == 0) and not c['has_rars']])

	for r in to_remove:
		print "removing torrent " + r['name']
		if take_action:
			t = r['torrent']
			tc.stop_torrent(t.id)
			tc.remove_torrent(t.hashString)
			pass
		else:
			print "not actually removing torrent as take action is false"

	to_move.extend(to_remove)

	print ''
	if to_move:
		print "moving %d dirs/files" % len(to_move)
		if take_action:
			move([c['name'] for c in to_move], complete_dir, out_dir)
			print ''
		else:
			print "not actually moving as take action is false"
	else:
		print 'nothing to move'
	print ''

	to_extract = [c for c in possibles if not c['torrent'] and c['has_rars']]
	printall(to_extract, "no torrent but has rars, to extract and/or delete:")

	to_extract_and_remove = [c for c in possibles if (c['torrent'] and c['torrent'].isFinished) and c['has_rars']]
	to_extract_and_remove.extend([c for c in possibles if (c['torrent'] and c['torrent'].status == "stopped" and c['torrent'].error == 0) and c['has_rars']])
	printall(to_extract_and_remove, "finished torrent with rars, to extract and remove torrent and data:")

	# tc.remove_torrent(ids, delete_data=False)

def find_rars(files):
	for f in files:
		if f.lower().endswith(".rar") or f.lower().endswith(".r00"):
			print "(found rar-like file %s)" % f
			if ".subpack." in f.lower():
				print "(looks like subpack, ignoring)"
			else:
				yield f


# figure out if we need to extract and do it
def extract(complete_dir, folder, take_action):

	path = complete_dir + "/" + folder
	print path
	if not dir_has_rars(path):
		print "no rars to extract - do recursive copy"
		return

	os.chdir(complete_dir)

	for root, subdirs, files in os.walk(folder):
		print "-- " + root
		rar = find_first_rar(files)
		if rar:
			print "extract " + root + "/" + rar + " to (dest folder)/" + root
			# copy other non-rar files
			# print re.findall(".rar$", )
			others = filter(lambda f: not f.endswith('rar') and not re.match(".*\.r\d\d$", f), files)
			print "copy to " + root, others

		else:
			if subdirs:
				print "dir has subdirs but no rars: mkdir"
			if not subdirs:
				print "dir has no subdirs: copy all"

	print "done; can delete " + folder

if __name__ == "__main__":
	take_action = False

	# extract(complete_dir, "The.Walking.Dead.S05E09.720p.HDTV.x264-KILLERS", take_action)               # simple ep
	# extract(complete_dir, "Parks.and.Recreation.S03.DVDRip.XviD-REWARD", take_action)                  # eps, subpack
	# extract(complete_dir, "Kingsman.The.Secret.Service.2014.UNCUT.720p.BluRay.x264-VETO", take_action)   # subs
	# extract(complete_dir, "Game.of.Thrones.S05E10.720p.HDTV.x264-IMMERSE", take_action)                  # no rars

	main(complete_dir, out_dir, take_action)
