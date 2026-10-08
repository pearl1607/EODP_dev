
# MAIN FUNCTION TO CALL THE L1C MODULE

from l1c.src.l1c import l1c


def main(auxdir, indir, outdir):
    # Initialise the ISM
    myL1c = l1c(auxdir, indir, outdir)
    myL1c.processModule()
