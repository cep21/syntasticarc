"""
Simple python wrapper to run arc lint on files and format the results in
a way that vim's makeprg and errorformat can parse.

Since arc lint can take a long time to run, it tries to be smart about
running itself inside a daemon.  It will:

    (1) Look inside /tmp/syntacticarc for a run result
    (2) If one exists, return it
    (3) Print out "Generating results"
    (4) Put itself inside a daemon and exit the main
    (5) Run lint
    (6) save restuls inside /tmp/syntacticarc

This lets you run the check frequently and not worry about blocking your
editor.  Uses daemonize.py, which I got from the intertubes at
http://code.activestate.com/recipes/278731-creating-a-daemon-the-python-way/
"""

__author__ = "Jack Lindamood"
__copyright__ = "Apache License, Version 2.0"

__version__ = "0.1"

from subprocess import Popen, PIPE
from daemonize import createDaemon
from optparse import OptionParser
import sys, json, pprint, pickle, hashlib, gzip, os

def runarc(filename):
  arc_binary = os.environ.get('SYNTACTIC_ARC', 'arc')
  if filename is None:
      cmd = Popen([arc_binary , 'lint', '--output' , 'json',
          '--advice', '--never-apply-patches'], stdout=PIPE)
  else:
      cmd = Popen([arc_binary , 'lint', '--lintall', '--output' , 'json',
          '--advice', '--never-apply-patches', filename], stdout=PIPE)
  cmd.wait()
  result = cmd.stdout.readlines()

  # Even with json output, arc prints non-json output for returncode 0
  if cmd.returncode == 0:
    return {}
  return json.loads(result[0])

def getArcResults(output):
  res = []
  for filename, results in output.iteritems():
    for err in results:
      severity = 'n'
      if len(err['severity']) > 0:
        severity = err['severity'][0]
        if severity == 'a':
          severity = 'n'
      desc = err['name'].strip()
      if desc == filename:
        desc = ""
      else:
        desc += ":"
      if 'desc' in err: # Requires patched arc
        desc += err['desc'].strip()
      res.append("%s:%d:%d:%s:%s" % (filename, int(err['line']), err['char'], severity, desc.strip()))
  return res

class OndiskDb():
    DB_FILE = '/tmp/syntacticarc'
    DAEMON_RUNNING = 'running'
    def getResults(self, filename):
      db = self.readDb()
      file_sha = hashlib.sha1(open(filename, 'r').read()).hexdigest()
      return db.get(filename, {}).get(file_sha, None)

    def readDb(self):
      try:
        f = gzip.open(self.DB_FILE, 'r+')
        return pickle.load(f)
      except:
        return {}

    def saveDb(self, filename, sha, res):
      old_db = self.readDb()
      if filename not in old_db:
        old_db[filename] = {}
      old_db[filename][sha] = res
      pickle.dump(old_db, gzip.open(self.DB_FILE, 'wb'))

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-b", "--blocking", dest="blocking",
    help="If set, will not use daemon", action='store_true', default=False)
  (options, args) = parser.parse_args()
  if len(args) > 1:
      parser.error("Incorrect number of args")
  if len(args) == 0:
      options.blocking = True

  if not options.blocking:
    db = OndiskDb()
    old_res = db.getResults(args[0])
  else:
    old_res = None
  if old_res is not None and old_res != OndiskDb.DAEMON_RUNNING:
    p = old_res
    print "\n".join(p).strip()
  else:
    if not options.blocking:
      orig_sha = hashlib.sha1(open(args[0], 'r').read()).hexdigest()
      dir = os.getcwd()
      print "%s:1:1:n:Generating results" % args[0]
      if old_res == 'running':
        sys.exit(0)
      db.saveDb(args[0], orig_sha, OndiskDb.DAEMON_RUNNING)
      sys.stdout.flush()
      import traceback
      createDaemon()
      os.chdir(dir) # Change back to original directory so arc works
    try:
        if len(args) == 0:
          arcres = runarc(None)
        else:
          arcres = runarc(args[0])

        p = getArcResults(arcres)
        if not options.blocking:
          db.saveDb(args[0], orig_sha, p)
        else:
          print "\n".join(p).strip()
    except:
        # Could be running in a daemon.  Put debug info in a file
        import traceback
        traceback.print_exc(file=open('/tmp/syntactic_debug', 'w'))
