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
  """
  Run arc lint on the filename provided.  If none, will
  lint the entire repository
  """
  arc_binary = os.environ.get('SYNTASTIC_ARC', 'arc')
  if filename is None:
      cmd = Popen([arc_binary , 'lint', '--output' , 'json'
          ], stdout=PIPE)
  else:
      cmd = Popen([arc_binary , 'lint', '--lintall', '--output' , 'json'
          , filename], stdout=PIPE)
  cmd.wait()
  result = cmd.stdout.readlines()

  # Even with json output, arc prints non-json output for returncode 0
  if cmd.returncode == 0:
    return {}
  res = {}
  for r in result:
      try:
          part = json.loads(r.strip())
      except ValueError as e:
          raise ValueError("Unable to json parse: " + r.strip())
      for filename, results in part.iteritems():
          if filename not in res:
              res[filename] = []
          res[filename].extend(results)

  return res

def toint_or_other(item, other):
    """
    Small helper to get around inconsistent lint output.
    Converts item to an int and returns other in failure.
    """
    try:
        return int(item)
    except:
        return other


def getArcResults(output, make_compatable):
  """
  Converts json output from arc into something vim can understand
  """
  res = []
  for filename, results in output.iteritems():
    for err in results:
      severity = 'n'
      if len(err['severity']) > 0:
        severity = err['severity'][0]
        if severity == 'a':
          severity = 'n'
      desc = [err['name'].strip()]
      if desc[0] == filename:
        desc = []
      desc.append(err.get('code', '').strip())
      desc.append(err.get('description', '').strip())
      if make_compatable:
        res.append(("%s:%d:%s" % (filename, toint_or_other(err['line'], 1), " ".join(desc))).replace("\n", " "))
      else:
        res.append(("%s:%d:%d:%s:%s" % (filename, toint_or_other(err['line'], 1), toint_or_other(err['char'], 1), severity, " ".join(desc))).replace("\n", " "))

  return res

class OndiskDb():
    """
    Helper class to store results on disc
    """
    DB_FILE = '/tmp/syntacticarc'
    DAEMON_RUNNING = 'running'
    def getResults(self, filename):
      """
      Gets previous results for running lint on a filename
      """
      db = self.readDb()
      file_sha = hashlib.sha1(open(filename, 'r').read()).hexdigest()
      return db.get(filename, {}).get(file_sha, None)

    def readDb(self):
      """
      Reads the entire DB and returns the results
      """
      try:
        f = gzip.open(self.DB_FILE, 'r+')
        return pickle.load(f)
      except:
        return {}

    def saveDb(self, filename, sha, res):
      """
      Appends to the run results for filename the result res
      """
      old_db = self.readDb()
      if filename not in old_db:
        old_db[filename] = {}
      old_db[filename][sha] = res
      pickle.dump(old_db, gzip.open(self.DB_FILE, 'wb'))

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-b", "--blocking", dest="blocking",
    help="If set, will not use daemon", action='store_true', default=False)
  parser.add_option("-m", "--make-compatable", dest="make_compatable",
    help="If set, will generate make compatable output.", action='store_true', default=False)
  (options, args) = parser.parse_args()
  if len(args) > 1:
      parser.error("Incorrect number of args")
  if len(args) == 0:
      options.blocking = True

  if options.make_compatable:
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
      # Give vim something to know we're running in the background
      print "%s:1:1:n:Generating results" % args[0]
      if old_res == 'running':
        sys.exit(0)
      db.saveDb(args[0], orig_sha, OndiskDb.DAEMON_RUNNING)
      sys.stdout.flush()
      import traceback
      createDaemon()
      # Change back to original directory so arc works
      os.chdir(dir)
    try:
        if len(args) == 0:
          arcres = runarc(None)
        else:
          arcres = runarc(args[0])

        p = getArcResults(arcres, options.make_compatable)
        if not options.blocking:
          db.saveDb(args[0], orig_sha, p)
        else:
          print "\n".join(p).strip()
    except:
        # Could be running in a daemon.  Put debug info in a file
        import traceback
        traceback.print_exc(file=open('/tmp/syntactic_debug', 'w'))
