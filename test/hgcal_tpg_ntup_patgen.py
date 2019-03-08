import ROOT
import sys
import random
import numpy as np

nBoards = 48
nLinks = 72
nFrames = 38

def init_mp7_dataspace():
  mp7data = np.zeros((nBoards, nLinks, nFrames), dtype=np.uint32)
  return mp7data

def get_mp7_data_coord(tcid):
  board = random.randint(0, nBoards-1)
  link = random.randint(0, nLinks-1)
  frame = random.randint(0, nFrames-1)
  byt = random.randint(0,3)
  return board, link, frame, byt

# initialize MP7 data space

mp7data = init_mp7_dataspace()

# TODO: load MP7 data space coordinate mappings

# load the input file

if len(sys.argv) < 3:
  print 'Usage:', sys.argv[0], '<in_ntup_rootfile> <out_filename_prefix>'
  sys.exit(2)

infn = sys.argv[1]
outpfx = sys.argv[2]

f = ROOT.TFile(infn)
t = f.Get('hgcalTriggerNtuplizer/HGCalTriggerNtuple')

# loop thru events

for k in xrange(t.GetEntries()):
  t.GetEntry(k)

  # Loop all trigger cells
  for i in xrange(t.tc_n):
    boardNo, linkNo, frameNo, byteNo = get_mp7_data_coord(t.tc_id[i])
    x = mp7data[boardNo][linkNo][frameNo]
    x = np.bitwise_and(x, np.bitwise_not(np.left_shift(np.uint32(0xff),
                                         8*byteNo)))
    x = np.bitwise_or(x, np.left_shift(
                           np.bitwise_and(np.uint32(0xff),
                                          np.uint32(t.tc_compressedCharge[i])),
                           8*byteNo))
    mp7data[boardNo][linkNo][frameNo] = x
    #print 'Uncomp =', hex(t.tc_compressedCharge[i]), ', byteNo = ', byteNo, ',  x =', hex(x)

  # produce mp7 output pattern text files

  for b in xrange(nBoards):
    outfn = outpfx + '_r' + str(t.run) + '_e' + str(t.event) + '_b' \
                   + '%02d'%b + '.mp7'
    of = open(outfn, 'w')
    of.write('Board MP7\n')
    qcline = 'Quad/Chan :'
    for i in xrange(nLinks):
        qcstr = '    q' + '%02d'%(i/4) + 'c' + str(i%4) + '  '
        qcline += qcstr
    of.write(qcline + '\n')
    linkline = 'Link      :'
    for i in xrange(nLinks):
      linkline += '     ' + '%2d'%i + '    '
    of.write(linkline + '\n')
    for i in xrange(nFrames):
      fline = 'Frame  %2d :' % i
      for j in xrange(nLinks):
        fline += ' 1v' + ('%08x' % mp7data[b][j][i])
      of.write(fline + '\n')
    of.close()

f.Close()

