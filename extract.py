import os
import sys
import re
from subprocess import call
import shutil

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

def copy_files(names, cwd, out_dir):
	for f in names:
		dest = os.path.join(out_dir, f)
		print "copying %s to %s" % (f, dest)
		shutil.copy2(os.path.join(cwd, f), dest)


# figure out if we need to extract and do it
def extract(complete_dir, folder, extract_dir, take_action=True):

	src = os.path.join(complete_dir, folder)
	dest = os.path.join(extract_dir, folder)

	# print path
	if not os.path.exists(src):
		print "path does not exist"
		return

	if not dir_has_rars(src):
		print "no rars to extract - do recursive copy"
		return

	if not os.path.exists(dest):
		os.makedirs(dest)

	print "Trying to unrar %s to %s" % (src, dest)

	for root, subdirs, files in os.walk(src):
		print "-- " + root
		relative_path = root.split(complete_dir + "/")[1]
		current_dest = os.path.join(extract_dir, relative_path)

		rar = find_first_rar(files)
		if rar:
			rar_path = os.path.join(root, rar)
			print "extract " + rar_path + " to " + current_dest

			if take_action:
				# extract with full path, do not overwrite
				code = call(["unrar", "x", '-o-', rar_path, current_dest])

				if code != 0 and code != 10:
					# 10 is "No files to extract" - can mean files already exists, or can't find dest.
					# raise Exception("call to unrar returned code %d" % code)
					print "ERROR: call to unrar returned code %d" % code
			else:
				print "take_action is False"

			# copy other non-rar files
			# print re.findall(".rar$", )
			others = filter(lambda f: not f.endswith('rar') and not re.match(".*\.r\d\d$", f), files)
			print "copy to " + root, others
			copy_files(others, root, current_dest)

		else:
			if subdirs:
				print "dir has subdirs but no rars: mkdir"
			if not subdirs:
				print "dir has no subdirs: copy all"
				print "copy to " + current_dest, files
				if not os.path.exists(current_dest):
					os.makedirs(current_dest)
				copy_files(files, root, current_dest)

	print "done extracting " + folder

if __name__ == "__main__":
	take_action = True

	complete_dir = '/home/joel/mac-mini.joel/Media Downloads/completed'
	extract_dir = "dest"

	# extract(complete_dir, "Twin.Peaks.S02E18.720p.BluRay.X264-REWARD", extract_dir, take_action)               # broken rar
	extract(complete_dir, "Adventure.Time.S06E03.720p.HDTV.x264-W4F", extract_dir, take_action)               # simple ep
	# extract(complete_dir, "The.Walking.Dead.S05E09.720p.HDTV.x264-KILLERS", extract_dir, take_action)               # simple ep
	# extract(complete_dir, "Parks.and.Recreation.S03.DVDRip.XviD-REWARD", take_action)                  # eps, subpack
	# extract(complete_dir, "Kingsman.The.Secret.Service.2014.UNCUT.720p.BluRay.x264-VETO", take_action)   # subs
	# extract(complete_dir, "Game.of.Thrones.S05E10.720p.HDTV.x264-IMMERSE", take_action)                  # no rars
