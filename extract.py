import os
import sys
import re
from subprocess import call
import shutil
import click

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
def extract(src, extract_dir, dry_run=False):

	# src = os.path.join(complete_dir, folder)
	dirname = os.path.dirname(src)
	basename = os.path.basename(src)
	dest = os.path.join(extract_dir, basename)

	# print path
	if not os.path.exists(src):
		print "path does not exist"
		return

	if not dir_has_rars(src):
		print "no rars found to extract - do recursive copy"
		return

	print "Trying to extract/copy %s to %s" % (src, dest)

	for root, subdirs, files in os.walk(src):
		print "-- " + root
		relative_path = root.split(dirname + "/")[1]
		current_dest = os.path.join(extract_dir, relative_path)

		if not os.path.exists(current_dest):
			os.makedirs(current_dest)

		rar = find_first_rar(files)
		if rar:
			rar_path = os.path.join(root, rar)
			print "extract " + rar_path + " to " + current_dest

			if not dry_run:
				# extract with full path, do not overwrite
				code = call(["unrar", "x", '-o-', rar_path, current_dest])

				if code != 0 and code != 10:
					# 10 is "No files to extract" - can mean files already exists, or can't find dest.
					# raise Exception("call to unrar returned code %d" % code)
					print "ERROR: call to unrar returned code %d" % code
			else:
				print "dry run only"

			# copy other non-rar files
			# print re.findall(".rar$", )
			others = filter(lambda f: not f.endswith('rar') and not re.match(".*\.r\d\d$", f), files)
			print "copy to " + root, others
			if not dry_run:
				copy_files(others, root, current_dest)
			else:
				print "dry run only"

		else:
			if subdirs:
				print "dir has subdirs but no rars"
			if not subdirs:
				print "dir has no subdirs: copy all"
				print "copy to " + current_dest, files
				if not dry_run:
					copy_files(files, root, current_dest)
				else:
					print "dry run only"

	print ''
	print "Done extracting " + basename

@click.command()
@click.option('--src', prompt=True, help='Folder to extract/copy')
@click.option('--dest', prompt=True, help='Destination')
@click.option('--dry_run', help='Don\'t actually make changes', default=False)
def main(src, dest, dry_run):
	extract(src, dest, dry_run)

if __name__ == '__main__':
	sys.exit(main())