import transmissionrpc
import os
import sys
import datetime

complete_dir = '/Users/joel/Media Downloads/completed'
out_dir = '/Users/joel/Media Downloads/out_tv'

tc = transmissionrpc.Client('localhost', port=9091)
torrents = tc.get_torrents()


def list_has_rars(files):
    for f in files:
        if f.lower().endswith(".rar") or f.lower().endswith(".r00"):
            print "found rar-like file %s" % f
            return True
    return False


def torrent_has_rars(t):
    return list_has_rars([f['name'] for f in t.files().values()])


print "torrents: ", len(torrents)
for t in torrents:
    print t.name
    print t.status
    # print t.isFinished  # finished seeding and/or stopped
    print "done:", t.percentDone
    print datetime.datetime.fromtimestamp(t.doneDate)
    # print t.files()
    print "has rars:", torrent_has_rars(t)

print [f['name'] for f in torrents[0].files().values()]
print ''
print [f['name'] for f in torrents[-1].files().values()]

sys.exit(0)

tnames = [t.name for t in tc.get_torrents()]

possibles = [x for x in os.listdir(complete_dir) if not x.startswith(".")]


def dir_has_rars(path):
    if not os.path.isdir(path): return False

    for root, subdirs, files in os.walk(path):
        if list_has_rars(files):
            return True
    return False


def print_possibles(possibles):
    for p in possibles:
        if p in tnames:
            print "Tx: " + p
            pass
        else:
            print "** NOT in Tx: " + p
            # TODO print if it has rars
            if os.path.isdir(p) and dir_has_rars(p):
                print "  ** HAS RARS"


print_possibles(possibles)

print ""
print "mkvs:"
mkvs = filter(lambda p: p.lower().endswith(".mkv"), possibles)

print_possibles(mkvs)


def move(names, cwd, out_dir):
    for f in names:
        print "moving %s to %s/%s" % (f, out_dir, f)
        os.rename("%s/%s" % (cwd, f), "%s/%s" % (out_dir, f))


print ''
print 'to move:'

to_move = [f for f in possibles if not f in tnames and not (os.path.isdir(f) and dir_has_rars(f))]

for f in to_move:
    print f

print ''

# move(to_move, complete_dir, out_dir)
# print ''
