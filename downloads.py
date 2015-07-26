import transmissionrpc
import os
import sys
import csv
from extract import extract, dir_has_rars

def move_files(names, cwd, out_dir):
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

			elif t and t.status == "seeding" or t.status == "downloading" or t.status == "download pending" or t.status == "checking":
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
			move_files([c['name'] for c in to_move], complete_dir, out_dir)
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


if __name__ == "__main__":
	take_action = False

	complete_dir = '/home/joel/mac-mini.joel/Media Downloads/completed'
	out_dir = '/home/joel/mac-mini.joel/Media Downloads/out_tv'
	extract_dir = "dest"

	main(complete_dir, out_dir, take_action)
